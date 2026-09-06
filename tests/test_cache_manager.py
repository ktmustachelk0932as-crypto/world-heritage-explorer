"""core.cache_manager のユニットテスト。"""

from __future__ import annotations

import pytest

from core import cache_manager


@pytest.fixture
def conn(tmp_path):
    connection = cache_manager.connect(tmp_path / "image_cache.sqlite")
    cache_manager.init_schema(connection)
    yield connection
    connection.close()


def test_upsert_and_get_roundtrip(conn) -> None:
    cache_manager.upsert(
        conn,
        {
            "site_id": 661,
            "wikidata_qid": "Q200092",
            "image_filename": "Himeji_Castle.jpg",
            "image_url": "https://example.org/thumb/Himeji_Castle.jpg",
            "source_page_url": "https://commons.wikimedia.org/wiki/File:Himeji_Castle.jpg",
            "license_short_name": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0",
            "artist": "A Photographer",
            "attribution_required": True,
            "status": "ok",
        },
    )

    row = cache_manager.get(conn, 661)
    assert row is not None
    assert row["status"] == "ok"
    assert row["image_url"].endswith("Himeji_Castle.jpg")
    assert row["attribution_required"] is True
    assert row["retrieved_at"]  # 自動補完される


def test_upsert_replaces_existing_row(conn) -> None:
    cache_manager.upsert(conn, {"site_id": 1, "status": "fetch_failed"})
    cache_manager.upsert(
        conn, {"site_id": 1, "status": "ok", "image_url": "https://example.org/x.jpg"}
    )

    row = cache_manager.get(conn, 1)
    assert row["status"] == "ok"
    assert row["image_url"] == "https://example.org/x.jpg"


def test_get_returns_none_for_unknown_site(conn) -> None:
    assert cache_manager.get(conn, 99999) is None


def test_pending_site_ids_skips_resolved_but_keeps_failed_and_new(conn) -> None:
    cache_manager.upsert(conn, {"site_id": 10, "status": "ok"})
    cache_manager.upsert(conn, {"site_id": 11, "status": "no_image"})
    cache_manager.upsert(conn, {"site_id": 12, "status": "excluded_license"})
    cache_manager.upsert(conn, {"site_id": 13, "status": "fetch_failed"})

    pending = cache_manager.pending_site_ids(conn, [10, 11, 12, 13, 14])

    assert pending == [13, 14]


def test_iter_ok_records_yields_only_ok_sorted(conn) -> None:
    cache_manager.upsert(conn, {"site_id": 30, "status": "ok"})
    cache_manager.upsert(conn, {"site_id": 20, "status": "ok"})
    cache_manager.upsert(conn, {"site_id": 25, "status": "no_image"})

    ids = [rec["site_id"] for rec in cache_manager.iter_ok_records(conn)]
    assert ids == [20, 30]
