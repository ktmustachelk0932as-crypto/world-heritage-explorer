"""core.image_fetcher のユニットテスト（API呼び出しはモックを使用）。"""

from __future__ import annotations

import pytest
import requests
from tenacity import wait_none

from core import image_fetcher
from core.image_fetcher import (
    MAX_ATTEMPTS,
    fetch_commons_image_info,
    sanitize_artist,
)


class _FakeResponse:
    def __init__(self, *, status_code: int = 200, payload: dict | None = None) -> None:
        self.status_code = status_code
        self._payload = payload or {}

    def json(self) -> dict:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


def _imageinfo_payload(extmetadata: dict) -> dict:
    return {
        "query": {
            "pages": [
                {
                    "title": "File:Example.jpg",
                    "imageinfo": [
                        {
                            "thumburl": "https://upload.example/thumb/Example.jpg",
                            "url": "https://upload.example/Example.jpg",
                            "descriptionshorturl": "https://commons.example/?curid=1",
                            "descriptionurl": "https://commons.example/File:Example.jpg",
                            "extmetadata": extmetadata,
                        }
                    ],
                }
            ]
        }
    }


def _meta(**pairs: str) -> dict:
    return {key: {"value": value} for key, value in pairs.items()}


@pytest.fixture(autouse=True)
def _no_retry_wait(monkeypatch: pytest.MonkeyPatch) -> None:
    """リトライ待機を無効化してテストを高速化する。"""
    monkeypatch.setattr(image_fetcher._get_with_retry.retry, "wait", wait_none())


@pytest.fixture
def calls() -> list[dict]:
    return []


def _install(monkeypatch: pytest.MonkeyPatch, calls: list, handler) -> None:
    def fake_get(url, params=None, headers=None, timeout=None):
        calls.append({"url": url, "params": params, "timeout": timeout})
        return handler(len(calls))

    monkeypatch.setattr(image_fetcher.requests, "get", fake_get)


def test_ok_image_parses_url_license_and_artist(
    monkeypatch: pytest.MonkeyPatch, calls: list
) -> None:
    payload = _imageinfo_payload(
        _meta(
            License="cc-by-sa-4.0",
            LicenseShortName="CC BY-SA 4.0",
            LicenseUrl="https://creativecommons.org/licenses/by-sa/4.0",
            Artist='<a href="//x">Jane&nbsp;Doe</a>',
            AttributionRequired="true",
        )
    )
    _install(monkeypatch, calls, lambda _n: _FakeResponse(payload=payload))

    info = fetch_commons_image_info("Example.jpg")

    assert info.status == "ok"
    assert info.image_url == "https://upload.example/thumb/Example.jpg"
    assert info.source_page_url == "https://commons.example/?curid=1"
    assert info.license_short_name == "CC BY-SA 4.0"
    assert info.artist == "Jane Doe"
    assert info.attribution_required is True
    assert len(calls) == 1
    assert calls[0]["timeout"] == image_fetcher.REQUEST_TIMEOUT_SECONDS


def test_missing_file_returns_no_image_without_retry(
    monkeypatch: pytest.MonkeyPatch, calls: list
) -> None:
    payload = {"query": {"pages": [{"title": "File:Nope.jpg", "missing": True}]}}
    _install(monkeypatch, calls, lambda _n: _FakeResponse(payload=payload))

    info = fetch_commons_image_info("Nope.jpg")

    assert info.status == "no_image"
    assert info.image_url == ""
    assert len(calls) == 1


def test_server_error_retries_then_fetch_failed(
    monkeypatch: pytest.MonkeyPatch, calls: list
) -> None:
    _install(monkeypatch, calls, lambda _n: _FakeResponse(status_code=503))

    info = fetch_commons_image_info("Flaky.jpg")

    assert info.status == "fetch_failed"
    assert len(calls) == MAX_ATTEMPTS


def test_timeout_retries_then_fetch_failed(
    monkeypatch: pytest.MonkeyPatch, calls: list
) -> None:
    def _raise(_n: int):
        raise requests.Timeout("slow")

    _install(monkeypatch, calls, _raise)

    info = fetch_commons_image_info("Slow.jpg")

    assert info.status == "fetch_failed"
    assert len(calls) == MAX_ATTEMPTS


def test_transient_error_then_success(
    monkeypatch: pytest.MonkeyPatch, calls: list
) -> None:
    payload = _imageinfo_payload(
        _meta(
            License="cc0",
            LicenseShortName="CC0",
            LicenseUrl="https://creativecommons.org/publicdomain/zero/1.0",
        )
    )

    def _handler(n: int):
        if n == 1:
            return _FakeResponse(status_code=500)
        return _FakeResponse(payload=payload)

    _install(monkeypatch, calls, _handler)

    info = fetch_commons_image_info("Eventually.jpg")

    assert info.status == "ok"
    assert len(calls) == 2


def test_restrictive_license_is_excluded(
    monkeypatch: pytest.MonkeyPatch, calls: list
) -> None:
    payload = _imageinfo_payload(
        _meta(
            License="cc-by-nc-2.0",
            LicenseShortName="CC BY-NC 2.0",
            LicenseUrl="https://creativecommons.org/licenses/by-nc/2.0",
        )
    )
    _install(monkeypatch, calls, lambda _n: _FakeResponse(payload=payload))

    info = fetch_commons_image_info("NonCommercial.jpg")

    assert info.status == "excluded_license"
    assert info.image_url == ""


def test_cc_by_without_license_url_is_excluded(
    monkeypatch: pytest.MonkeyPatch, calls: list
) -> None:
    payload = _imageinfo_payload(
        _meta(License="cc-by-4.0", LicenseShortName="CC BY 4.0")
    )
    _install(monkeypatch, calls, lambda _n: _FakeResponse(payload=payload))

    info = fetch_commons_image_info("NoUrl.jpg")

    assert info.status == "excluded_license"


def test_public_domain_without_license_url_is_allowed(
    monkeypatch: pytest.MonkeyPatch, calls: list
) -> None:
    payload = _imageinfo_payload(_meta(License="pd", LicenseShortName="Public domain"))
    _install(monkeypatch, calls, lambda _n: _FakeResponse(payload=payload))

    info = fetch_commons_image_info("Old.jpg")

    assert info.status == "ok"


_PD_BOILERPLATE = (
    "Public domain Public domain false false I, the copyright holder of "
    "this work, release this work into the public domain . This applies "
    "worldwide."
)
_ASSUMED_AUTHOR = (
    "No machine-readable author provided. Dom2002 assumed (based on copyright claims)."
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ('<a href="//x">Jane&nbsp;Doe</a>', "Jane Doe"),
        ("CEphoto, Uwe Aranas", "CEphoto, Uwe Aranas"),
        ("", ""),
        (_PD_BOILERPLATE, ""),
        (_ASSUMED_AUTHOR, "Dom2002"),
        ("Unknown author", ""),
    ],
)
def test_sanitize_artist(raw: str, expected: str) -> None:
    assert sanitize_artist(raw) == expected


def test_ok_image_sanitizes_boilerplate_artist(
    monkeypatch: pytest.MonkeyPatch, calls: list
) -> None:
    payload = _imageinfo_payload(
        _meta(
            License="pd",
            LicenseShortName="Public domain",
            Artist=(
                "No machine-readable author provided. Foo assumed "
                "(based on copyright claims)."
            ),
        )
    )
    _install(monkeypatch, calls, lambda _n: _FakeResponse(payload=payload))

    info = fetch_commons_image_info("Old.jpg")

    assert info.status == "ok"
    assert info.artist == "Foo"
