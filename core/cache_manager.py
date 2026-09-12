"""SQLite キャッシュ（data/cache/image_cache.sqlite）の読み書き。

``site_id`` ごとに画像 URL・ライセンス・作者情報・取得ステータスを永続化し、
``scripts/prefetch_images.py`` の再実行時に取得済み分の再リクエストを防ぐ。
このキャッシュはローカル作業用（``.gitignore`` 済み）。デプロイ時に配布されるのは
ここから書き出す ``data/processed/heritage_images.parquet`` のスナップショット。
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime
from pathlib import Path

DEFAULT_DB_PATH: Path = (
    Path(__file__).resolve().parents[1] / "data" / "cache" / "image_cache.sqlite"
)

# status: ok（画像あり） / no_image（P18 なし・Commons に無い） /
#         excluded_license（ライセンス不許可） / fetch_failed（一時的失敗、再取得対象）
_RESOLVED_STATUSES: frozenset[str] = frozenset({"ok", "no_image", "excluded_license"})

_SCHEMA = """
CREATE TABLE IF NOT EXISTS image_cache (
    site_id              INTEGER PRIMARY KEY,
    wikidata_qid         TEXT,
    image_filename       TEXT,
    image_url            TEXT,
    source_page_url      TEXT,
    license_short_name   TEXT,
    license_url          TEXT,
    artist               TEXT,
    attribution_required INTEGER,
    status               TEXT NOT NULL,
    retrieved_at         TEXT NOT NULL
)
"""

_COLUMNS: tuple[str, ...] = (
    "site_id",
    "wikidata_qid",
    "image_filename",
    "image_url",
    "source_page_url",
    "license_short_name",
    "license_url",
    "artist",
    "attribution_required",
    "status",
    "retrieved_at",
)


def connect(path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """キャッシュ DB へ接続する（親ディレクトリが無ければ作成、行を dict 風に返す）。"""
    path = Path(path)
    if path != Path(":memory:"):
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """テーブルが無ければ作成する。"""
    conn.execute(_SCHEMA)
    conn.commit()


def get(conn: sqlite3.Connection, site_id: int) -> dict | None:
    """1 遺産分のキャッシュ行を返す（無ければ ``None``）。"""
    row = conn.execute(
        "SELECT * FROM image_cache WHERE site_id = ?", (int(site_id),)
    ).fetchone()
    return _row_to_dict(row) if row is not None else None


def upsert(conn: sqlite3.Connection, record: dict) -> None:
    """1 遺産分のキャッシュ行を挿入または置換する。

    ``record`` は少なくとも ``site_id`` と ``status`` を含む。``retrieved_at`` が
    無ければ現在時刻（UTC・ISO8601）を補う。
    """
    payload = {col: record.get(col) for col in _COLUMNS}
    payload["site_id"] = int(record["site_id"])
    payload["status"] = str(record["status"])
    payload["retrieved_at"] = record.get("retrieved_at") or _now_iso()
    if payload["attribution_required"] is not None:
        payload["attribution_required"] = int(bool(payload["attribution_required"]))

    placeholders = ", ".join(f":{col}" for col in _COLUMNS)
    conn.execute(
        f"INSERT OR REPLACE INTO image_cache ({', '.join(_COLUMNS)}) "
        f"VALUES ({placeholders})",
        payload,
    )
    conn.commit()


def iter_ok_records(conn: sqlite3.Connection) -> Iterator[dict]:
    """``status = 'ok'`` の行を ``site_id`` 昇順で返す。"""
    cursor = conn.execute(
        "SELECT * FROM image_cache WHERE status = 'ok' ORDER BY site_id"
    )
    for row in cursor:
        yield _row_to_dict(row)


def pending_site_ids(conn: sqlite3.Connection, all_ids: Sequence[int]) -> list[int]:
    """再取得が必要な ``site_id``（未取得、または ``status = 'fetch_failed'``）を返す。

    ``ok`` / ``no_image`` / ``excluded_license`` は確定済みとしてスキップする。
    """
    resolved = {
        int(row["site_id"])
        for row in conn.execute(
            "SELECT site_id FROM image_cache WHERE status IN "
            f"({', '.join('?' * len(_RESOLVED_STATUSES))})",
            tuple(_RESOLVED_STATUSES),
        )
    }
    return [int(sid) for sid in all_ids if int(sid) not in resolved]


def _row_to_dict(row: sqlite3.Row) -> dict:
    data = dict(row)
    if data.get("attribution_required") is not None:
        data["attribution_required"] = bool(data["attribution_required"])
    return data


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")
