"""全遺産分の代表画像 URL を事前一括取得し、キャッシュ DB とスナップショットへ保存する。

ランタイム（Streamlit Cloud）での Wikimedia API 呼び出しを原則ゼロにするための事前処理
（計画書11.2）。

処理:
1. ``heritage_sites.parquet`` から ``site_id`` / ``wikidata_qid`` / ``image_filename`` を読む
2. ``data/cache/image_cache.sqlite`` を開き、未取得（または前回失敗）の遺産のみ対象にする
3. ``image_filename`` が無い遺産は API を呼ばず ``no_image`` として記録
4. 残りを逐次処理（リクエスト間 100〜200ms スリープ、``core.image_fetcher`` がリトライ）
5. ``status = 'ok'`` の行から ``data/processed/heritage_images.parquet`` を書き出す（コミット対象）
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import cache_manager
from core.data_loader import IMAGE_COLUMNS, IMAGES_PARQUET_PATH, load_heritage_sites
from core.env import load_env_file
from core.image_fetcher import fetch_commons_image_info

LOGGER = logging.getLogger(__name__)

# Wikimedia のエチケットポリシー遵守のためのリクエスト間インターバル（秒）。
# 匿名アクセスは 429 になりやすいため長めに取る（連絡先付き User-Agent 推奨）。
_REQUEST_INTERVAL_SECONDS: float = 0.5


def run(*, limit: int | None = None, force: bool = False) -> dict[str, int]:
    """事前取得を実行し、ステータス別の件数を返す。"""
    sites = load_heritage_sites()[["site_id", "wikidata_qid", "image_filename"]]
    all_ids = [int(sid) for sid in sites["site_id"]]

    conn = cache_manager.connect()
    cache_manager.init_schema(conn)

    if force:
        targets = all_ids
    else:
        targets = cache_manager.pending_site_ids(conn, all_ids)
    if limit is not None:
        targets = targets[:limit]

    target_set = set(targets)
    rows = sites[sites["site_id"].isin(target_set)]
    LOGGER.info(
        "対象 %d 件 / 全 %d 件（force=%s, limit=%s）",
        len(rows),
        len(all_ids),
        force,
        limit,
    )

    counts = {"ok": 0, "no_image": 0, "excluded_license": 0, "fetch_failed": 0}
    for position, row in enumerate(rows.itertuples(index=False), start=1):
        site_id = int(row.site_id)
        filename = str(row.image_filename or "").strip()
        qid = str(row.wikidata_qid or "").strip()

        if not filename:
            record = {"site_id": site_id, "wikidata_qid": qid, "status": "no_image"}
        else:
            info = fetch_commons_image_info(filename)
            record = {
                "site_id": site_id,
                "wikidata_qid": qid,
                "image_filename": filename,
                "image_url": info.image_url,
                "source_page_url": info.source_page_url,
                "license_short_name": info.license_short_name,
                "license_url": info.license_url,
                "artist": info.artist,
                "attribution_required": info.attribution_required,
                "status": info.status,
            }
            time.sleep(_REQUEST_INTERVAL_SECONDS)

        try:
            cache_manager.upsert(conn, record)
        except Exception:
            LOGGER.exception("キャッシュ書き込みに失敗しました (site_id=%d)", site_id)
            record["status"] = "fetch_failed"

        counts[record["status"]] = counts.get(record["status"], 0) + 1
        if position % 100 == 0:
            LOGGER.info("進捗 %d / %d", position, len(rows))

    export_snapshot(conn)
    conn.close()
    return counts


def export_snapshot(conn) -> Path:
    """``status = 'ok'`` の行から画像スナップショット parquet を書き出す。"""
    records = [
        {col: rec.get(col) for col in IMAGE_COLUMNS}
        for rec in cache_manager.iter_ok_records(conn)
    ]
    df = pd.DataFrame(records, columns=list(IMAGE_COLUMNS))
    IMAGES_PARQUET_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(IMAGES_PARQUET_PATH, index=False)
    LOGGER.info(
        "スナップショットを保存しました: %s（%d 件）", IMAGES_PARQUET_PATH, len(df)
    )
    return IMAGES_PARQUET_PATH


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--limit", type=int, default=None, help="処理する遺産数の上限（動作確認用）"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="取得済み（ok / no_image / excluded_license）も含めて再取得する",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    load_env_file()
    args = _parse_args(argv)
    counts = run(limit=args.limit, force=args.force)
    total = sum(counts.values())
    print(
        f"完了: 計 {total} 件 "
        f"(ok={counts['ok']}, no_image={counts['no_image']}, "
        f"excluded_license={counts['excluded_license']}, "
        f"fetch_failed={counts['fetch_failed']})"
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    try:
        main()
    except Exception:
        LOGGER.exception("画像の事前取得に失敗しました。")
        sys.exit(1)
