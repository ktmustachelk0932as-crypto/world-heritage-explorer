"""詳細情報パネル（名称・登録年・国・分類・登録基準のテキスト＋代表画像）。"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pandas as pd
import streamlit as st

from app.components.map_view import CATEGORY_LABELS_JA
from core.criteria import describe_criteria

_UNESCO_SITE_URL = "https://whc.unesco.org/en/list/{site_id}"

_CATEGORY_ICONS: dict[str, str] = {
    "Cultural": "🏛️",
    "Natural": "🌲",
    "Mixed": "🌏",
}


def render_detail_panel(
    site: pd.Series | None,
    image: pd.Series | Mapping[str, Any] | None = None,
) -> None:
    """選択された世界遺産サイトの詳細（テキスト＋代表画像）を表示する。

    Args:
        site: ``core.data_loader.load_heritage_sites`` の 1 行。未選択時は ``None``。
        image: ``core.data_loader.load_heritage_images`` の該当行（``image_url`` 等）。
            画像が無い / 取得できない場合は ``None``。
    """
    st.subheader("詳細情報")

    if site is None:
        st.info("地図上のマーカーをクリックすると詳細が表示されます。")
        return

    category_key = str(site["category"])
    category = CATEGORY_LABELS_JA.get(category_key, category_key)
    criteria = str(site.get("criteria", "") or "")

    st.markdown(f"### {site['name']}")
    _render_image(image, category_key)
    st.markdown(f"**国 / 地域**: {site['country']}")
    st.markdown(f"**登録年**: {int(site['date_inscribed'])}")
    st.markdown(f"**分類**: {category}")
    if criteria:
        st.markdown(f"**登録基準**: {criteria}")
        for token, description in describe_criteria(criteria):
            st.caption(f"{token} {description}")

    site_id = int(site["site_id"])
    st.markdown(f"[UNESCO 公式ページ]({_UNESCO_SITE_URL.format(site_id=site_id)})")
    st.caption(f"UNESCO ID: {site_id}")


def _render_image(
    image: pd.Series | Mapping[str, Any] | None, category_key: str
) -> None:
    """代表画像とクレジット行を表示する。画像が無ければプレースホルダーを出す。"""
    url = _value(image, "image_url")
    if not url:
        icon = _CATEGORY_ICONS.get(category_key, "🖼️")
        st.markdown(
            f"<div style='font-size:2.5rem'>{icon}</div>", unsafe_allow_html=True
        )
        st.caption("代表画像は取得できませんでした")
        return

    st.image(url, width="stretch")
    st.caption(_credit_line(image))


def _credit_line(image: pd.Series | Mapping[str, Any] | None) -> str:
    artist = _value(image, "artist")
    license_name = _value(image, "license_short_name")
    license_url = _value(image, "license_url")
    source_url = _value(image, "source_page_url")

    parts: list[str] = []
    if artist:
        parts.append(str(artist))
    if license_name:
        parts.append(
            f"[{license_name}]({license_url})" if license_url else license_name
        )

    if parts:
        credit = " / ".join(parts)
        if source_url:
            credit += f"（[Wikimedia Commons]({source_url})）"
        return credit
    # 作者名・ライセンス名が無い場合は出典表記を二重に出さない。
    if source_url:
        return f"出典: [Wikimedia Commons]({source_url})"
    return "出典: Wikimedia Commons"


def _value(image: pd.Series | Mapping[str, Any] | None, key: str) -> Any:
    if image is None:
        return ""
    try:
        raw = image[key]
    except (KeyError, IndexError, TypeError):
        return ""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return ""
    return raw
