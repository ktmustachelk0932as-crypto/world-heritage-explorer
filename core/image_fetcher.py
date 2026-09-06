"""Wikimedia Commons API による代表画像 URL・ライセンス情報の取得。

計画書11章の方針に従う：
- User-Agent に連絡先情報を含める（``core.user_agent.build_user_agent``）
- 逐次実行（並列呼び出しをしない）。リクエスト間インターバルは呼び出し側の責務
- 一時的失敗（タイムアウト・5xx）は指数バックオフで最大3回リトライ（``tenacity``）
- 恒久的失敗（画像なし・404）はリトライせずフォールバック
- タイムアウトを明示的に設定（5秒）
- ライセンス・作者情報を取得し、UI でのクレジット表示に使う（11.6）
"""

from __future__ import annotations

import html
import logging
import re
import time
from dataclasses import dataclass
from typing import Literal

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from core.user_agent import build_user_agent

LOGGER = logging.getLogger(__name__)

COMMONS_API_ENDPOINT = "https://commons.wikimedia.org/w/api.php"
REQUEST_TIMEOUT_SECONDS: float = 5.0
THUMB_WIDTH: int = 800
MAX_ATTEMPTS: int = 4

# リトライ待機。テストではモジュール属性 ``_get_with_retry.retry.wait`` を
# ``tenacity.wait_none()`` に差し替えて即時失敗させる。429（レート制限）でも
# ここで待つため、上限は長めに取る。
_RETRY_WAIT = wait_exponential(multiplier=1, max=30)

# 一時的失敗としてリトライする HTTP ステータス（429=レート制限, 5xx=サーバ側障害）。
_RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({429, 500, 502, 503, 504})

# 著作者表示が容易な自由ライセンスのみ許可する（前方一致・空白無視・小文字化して比較）。
_ALLOWED_LICENSE_PREFIXES: tuple[str, ...] = (
    "cc0",
    "cc-by",
    "cc by",
    "pd",
    "publicdomain",
    "public domain",
)
# ライセンス URL が無くても許可するパブリックドメイン系の機械名。
_PUBLIC_DOMAIN_PREFIXES: tuple[str, ...] = ("cc0", "pd", "publicdomain")
# 非営利（NC）・改変禁止（ND）は自由ライセンスとして扱わない（正規化後に部分一致で判定）。
_RESTRICTED_LICENSE_MARKERS: tuple[str, ...] = (
    "-nc-",
    "-nc",
    "-nd-",
    "-nd",
    "noncommercial",
    "noderiv",
)

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

ImageStatus = Literal["ok", "no_image", "excluded_license", "fetch_failed"]


class _RetryableError(Exception):
    """5xx など、リトライする価値のある一時的失敗。"""


@dataclass(frozen=True)
class ImageInfo:
    """1 遺産分の代表画像情報。``status`` 以外は ``status == "ok"`` のときのみ有効。"""

    status: ImageStatus
    image_url: str = ""
    source_page_url: str = ""
    license_short_name: str = ""
    license_url: str = ""
    artist: str = ""
    attribution_required: bool = False


@retry(
    stop=stop_after_attempt(MAX_ATTEMPTS),
    wait=_RETRY_WAIT,
    retry=retry_if_exception_type((requests.Timeout, _RetryableError)),
    reraise=True,
)
def _get_with_retry(params: dict) -> requests.Response:
    """Commons API へ GET する（タイムアウト・429・5xx は最大 ``MAX_ATTEMPTS`` 回リトライ）。"""
    response = requests.get(
        COMMONS_API_ENDPOINT,
        params=params,
        headers={"User-Agent": build_user_agent()},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if response.status_code in _RETRYABLE_STATUS_CODES:
        raise _RetryableError(f"HTTP {response.status_code} from Commons API")
    response.raise_for_status()
    return response


def fetch_commons_image_info(filename: str) -> ImageInfo:
    """Wikimedia Commons のファイル名から代表画像情報を取得する。

    Args:
        filename: ``File:`` 接頭辞を含まない Commons のファイル名
            （例: ``Himeji_Castle_The_Keep_Towers.jpg``）。

    Returns:
        取得結果。失敗しても例外は送出せず、``status`` で区別する
        （``ok`` / ``no_image`` / ``excluded_license`` / ``fetch_failed``）。
    """
    started = time.monotonic()
    try:
        response = _get_with_retry(_build_params(filename))
        payload = response.json()
    except (requests.RequestException, _RetryableError, ValueError) as exc:
        LOGGER.warning("画像情報の取得に失敗しました (%s): %s", filename, exc)
        return ImageInfo(status="fetch_failed")

    elapsed_ms = (time.monotonic() - started) * 1000
    pages = payload.get("query", {}).get("pages", [])
    page = pages[0] if pages else {}
    image_infos = page.get("imageinfo") or []
    if page.get("missing") or not image_infos:
        LOGGER.info("画像が存在しません (%s, %.0fms)", filename, elapsed_ms)
        return ImageInfo(status="no_image")

    info = image_infos[0]
    meta = info.get("extmetadata", {})
    license_short = _meta_value(meta, "LicenseShortName")
    license_url = _meta_value(meta, "LicenseUrl")

    if not _license_allowed(meta, license_url):
        LOGGER.info(
            "ライセンス不許可のため除外 (%s): %s", filename, license_short or "不明"
        )
        return ImageInfo(status="excluded_license", license_short_name=license_short)

    LOGGER.info("画像情報を取得しました (%s, %.0fms)", filename, elapsed_ms)
    return ImageInfo(
        status="ok",
        image_url=info.get("thumburl") or info.get("url", ""),
        source_page_url=info.get("descriptionshorturl")
        or info.get("descriptionurl", ""),
        license_short_name=license_short,
        license_url=license_url,
        artist=_strip_html(_meta_value(meta, "Artist")),
        attribution_required=_meta_value(meta, "AttributionRequired").lower() == "true",
    )


def _build_params(filename: str) -> dict:
    return {
        "action": "query",
        "titles": f"File:{filename}",
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "iiurlwidth": THUMB_WIDTH,
        "format": "json",
        "formatversion": 2,
    }


def _meta_value(meta: dict, key: str) -> str:
    entry = meta.get(key)
    if not isinstance(entry, dict):
        return ""
    return str(entry.get("value", "")).strip()


def _license_allowed(meta: dict, license_url: str) -> bool:
    """著作者表示が容易な自由ライセンスかどうかを判定する（11.6）。"""
    machine = _meta_value(meta, "License").lower()
    short = _meta_value(meta, "LicenseShortName").lower()
    candidates = [_normalize(c) for c in (machine, short) if c]
    if not candidates:
        return False
    if any(marker in c for c in candidates for marker in _RESTRICTED_LICENSE_MARKERS):
        return False
    if not any(
        c.startswith(_normalize(p))
        for c in candidates
        for p in _ALLOWED_LICENSE_PREFIXES
    ):
        return False
    # CC BY 系はライセンス URL 必須。パブリックドメイン系は URL 欠落を許容する。
    is_public_domain = any(
        c.startswith(_normalize(p)) for c in candidates for p in _PUBLIC_DOMAIN_PREFIXES
    )
    return bool(license_url) or is_public_domain


def _normalize(value: str) -> str:
    return value.replace(" ", "").replace("_", "-").lower()


def _strip_html(raw: str) -> str:
    if not raw:
        return ""
    return _WS_RE.sub(" ", html.unescape(_TAG_RE.sub(" ", raw))).strip()
