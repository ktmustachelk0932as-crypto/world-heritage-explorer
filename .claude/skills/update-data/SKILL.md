---
name: update-data
description: 世界遺産データ更新パイプラインを一括実行する（生データ取得 → データセット構築 → 画像URL事前取得 → pytest検証）
---

# データ更新パイプライン

以下をこの順で実行する。各ステップが失敗したら**そこで中断し、エラー内容を報告する**（次のステップに進まない）。

1. `python3 scripts/fetch_raw_data.py` — 生データ（Wikidata Query Service の SPARQL 結果）を `data/raw/` へダウンロード
2. `python3 scripts/build_dataset.py` — `data/raw/` → `data/processed/heritage_sites.parquet` へ変換
3. `python3 scripts/prefetch_images.py` — 全遺産分の画像URL・ライセンス情報を Wikimedia Commons から事前取得し、キャッシュDBと `data/processed/heritage_images.parquet` へ保存（逐次アクセスのため時間がかかる）
4. `pytest` — 全テストがグリーンであることを確認

完了したら、各ステップの結果（取得件数・生成ファイル・テスト結果）を簡潔にまとめて報告する。
