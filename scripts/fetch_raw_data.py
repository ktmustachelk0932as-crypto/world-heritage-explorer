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
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.env import load_env_file
from core.user_agent import build_user_agent

LOGGER = logging.getLogger(__name__)

RAW_DIR: Path = Path(__file__).resolve().parents[1] / "data" / "raw"
OUTPUT_PATH: Path = RAW_DIR / "wikidata_world_heritage_sites.json"

WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
REQUEST_TIMEOUT_SECONDS: float = 90.0

# P1435=遺産指定, Q9259=世界遺産, P757=WHC参照番号, P625=座標,
# P17=国, P297=ISO 3166-1 alpha-2, P580=登録（開始）年, P2614=世界遺産登録基準,
# P18=画像（Wikimedia Commons のファイル名。代表画像の取得に使う）
#
# P2614（登録基準）は、P1435文の修飾子（pq:）としてよりも、項目への直接ステートメント
# （wdt:）として付与されている方が実際には多い（Wikidataの実データで確認済み：
# 修飾子経由のみだと約24%しかカバーできないが、直接ステートメントとのUNIONで
# 約98%までカバー率が上がる）。そのため両方をUNIONで取得する。
# ``?itemLabelJa`` は遺産名の日本語表示用。共通の ``wikibase:label`` サービスを
# ``"ja,en"`` にすると ``?criteriaLabel``（(i)〜(x)）まで日本語化してしまい、
# build_dataset 側の登録基準の完全一致判定が壊れて全遺産が脱落する。そのため
# item ラベル専用の ``rdfs:label`` + 言語フィルタで隔離して取得する。日本語
# ラベルが無い項目は束縛されない（build_dataset 側で英語名にフォールバック）。
SPARQL_QUERY = """
SELECT ?item ?itemLabel ?itemLabelJa ?whcId ?coord ?inscribedDate
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
  OPTIONAL { ?item rdfs:label ?itemLabelJa . FILTER(LANG(?itemLabelJa) = "ja") }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

# 画像（P18）はメインクエリに含めると国×登録基準×画像の直積で結果が肥大化し、
# WDQS のストリーミング上限（結果が途中で切れる）に達するため、別クエリで取得して
# build_dataset.py 側で ?item / ?whcId をキーに突き合わせる。
IMAGE_SPARQL_QUERY = """
SELECT ?item ?whcId ?image WHERE {
  ?item p:P1435 ?stmt .
  ?stmt ps:P1435 wd:Q9259 .
  ?stmt wikibase:rank ?rank .
  FILTER(?rank != wikibase:DeprecatedRank)
  ?item wdt:P757 ?whcId .
  ?item wdt:P18 ?image .
}
"""


def _run_query(query: str, label: str) -> list[dict]:
    """SPARQL を実行し ``results.bindings`` を返す。"""
    headers = {
        "User-Agent": build_user_agent(),
        "Accept": "application/sparql-results+json",
    }
    LOGGER.info("Wikidata Query Service へ問い合わせています（%s）", label)
    response = requests.get(
        WIKIDATA_SPARQL_ENDPOINT,
        params={"query": query, "format": "json"},
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    bindings = response.json().get("results", {}).get("bindings", [])
    LOGGER.info("取得件数（%s）: %d 行", label, len(bindings))
    return bindings


def fetch_world_heritage_bindings() -> dict:
    """世界遺産の主データと画像（P18）を取得し、束縛行を結合した JSON を返す。

    画像クエリの結果行（``item`` / ``whcId`` / ``image`` のみ）を主クエリの
    束縛リストへ追記する。build_dataset.py の集約はキー欠損に強いので、
    画像だけの行はそのまま画像情報の補完に使える。

    Raises:
        requests.HTTPError: HTTPエラーステータスが返った場合。
        requests.Timeout: タイムアウトした場合。
        RuntimeError: 主クエリの結果が空の場合。
    """
    main_bindings = _run_query(SPARQL_QUERY, "主データ")
    if not main_bindings:
        raise RuntimeError(
            "SPARQLクエリの結果が空でした。クエリ内容を確認してください。"
        )
    image_bindings = _run_query(IMAGE_SPARQL_QUERY, "画像 P18")
    return {"results": {"bindings": [*main_bindings, *image_bindings]}}


def save_raw_json(payload: dict, output_path: Path) -> None:
    """レスポンスJSONをそのまま保存する（変換は行わない）。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    LOGGER.info("保存しました: %s", output_path)


def main() -> None:
    load_env_file()
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
