"""生データ（Wikidata Query Service）を data/raw/ へダウンロードするスクリプト。

UNESCO DataHub（data.unesco.org）には座標付きの世界遺産一覧データセットが存在せず、
whc.unesco.org はCloudflareのBot対策により自動取得できないため、代替としてWikidataの
SPARQLエンドポイントから世界遺産（Q9259）の指定を受けた項目を取得する。

このスクリプトはSPARQLクエリの実行とレスポンスJSONの保存のみを行い、
重複排除・分類導出等の変換ロジックは持たない（変換は build_dataset.py が担う）。
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

import requests

LOGGER = logging.getLogger(__name__)

RAW_DIR: Path = Path(__file__).resolve().parents[1] / "data" / "raw"
OUTPUT_PATH: Path = RAW_DIR / "wikidata_world_heritage_sites.json"

WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
REQUEST_TIMEOUT_SECONDS: float = 90.0

# P1435=遺産指定, Q9259=世界遺産, P757=WHC参照番号, P625=座標,
# P17=国, P297=ISO 3166-1 alpha-2, P580=登録（開始）年, P2614=世界遺産登録基準
#
# P2614（登録基準）は、P1435文の修飾子（pq:）としてよりも、項目への直接ステートメント
# （wdt:）として付与されている方が実際には多い（Wikidataの実データで確認済み：
# 修飾子経由のみだと約24%しかカバーできないが、直接ステートメントとのUNIONで
# 約98%までカバー率が上がる）。そのため両方をUNIONで取得する。
SPARQL_QUERY = """
SELECT ?item ?itemLabel ?whcId ?coord ?inscribedDate
       ?country ?countryLabel ?isoCode ?criteria ?criteriaLabel WHERE {
  ?item p:P1435 ?stmt .
  ?stmt ps:P1435 wd:Q9259 .
  ?stmt wikibase:rank ?rank .
  FILTER(?rank != wikibase:DeprecatedRank)
  OPTIONAL { ?stmt pq:P580 ?inscribedDate . }
  OPTIONAL {
    { ?item wdt:P2614 ?criteria . } UNION { ?stmt pq:P2614 ?criteria . }
  }
  OPTIONAL { ?item wdt:P757 ?whcId . }
  OPTIONAL { ?item wdt:P625 ?coord . }
  OPTIONAL {
    ?item wdt:P17 ?country .
    OPTIONAL { ?country wdt:P297 ?isoCode . }
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""


def build_user_agent() -> str:
    """Wikimediaの利用規約に沿い、連絡先を含むUser-Agentを組み立てる。

    環境変数 WIKIMEDIA_CONTACT_EMAIL が未設定でも処理は継続する（警告ログのみ）。
    """
    contact = os.environ.get("WIKIMEDIA_CONTACT_EMAIL", "").strip()
    if not contact:
        LOGGER.warning(
            "WIKIMEDIA_CONTACT_EMAIL が未設定です。"
            "Wikimediaの利用規約では連絡先を含むUser-Agentが推奨されています。"
        )
        return "world-heritage-explorer/0.1 (no contact email set)"
    return f"world-heritage-explorer/0.1 (contact: {contact})"


def fetch_world_heritage_bindings() -> dict:
    """WikidataのSPARQLエンドポイントへ問い合わせ、レスポンスJSONを返す。

    Raises:
        requests.HTTPError: HTTPエラーステータスが返った場合。
        requests.Timeout: タイムアウトした場合。
        RuntimeError: レスポンスに束縛データが含まれない場合。
    """
    headers = {
        "User-Agent": build_user_agent(),
        "Accept": "application/sparql-results+json",
    }
    LOGGER.info(
        "Wikidata Query Serviceへ問い合わせています: %s", WIKIDATA_SPARQL_ENDPOINT
    )
    response = requests.get(
        WIKIDATA_SPARQL_ENDPOINT,
        params={"query": SPARQL_QUERY, "format": "json"},
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = response.json()
    bindings = payload.get("results", {}).get("bindings", [])
    if not bindings:
        raise RuntimeError(
            "SPARQLクエリの結果が空でした。クエリ内容を確認してください。"
        )
    LOGGER.info("取得件数（構成資産・重複含む）: %d 行", len(bindings))
    return payload


def save_raw_json(payload: dict, output_path: Path) -> None:
    """レスポンスJSONをそのまま保存する（変換は行わない）。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    LOGGER.info("保存しました: %s", output_path)


def main() -> None:
    payload = fetch_world_heritage_bindings()
    save_raw_json(payload, OUTPUT_PATH)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    try:
        main()
    except Exception:
        LOGGER.exception("生データの取得に失敗しました。")
        sys.exit(1)
