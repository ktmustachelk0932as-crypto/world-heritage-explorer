"""data/raw/ → data/processed/heritage_sites.parquet への変換バッチ。

Wikidataから取得した生データ（SPARQL結果JSON）は、複合遺産の構成資産にも
親遺産と同じWHC参照番号（枝番付き）が重複して付与されているため、
遺産単位への重複排除・代表アイテムの選定・分類（文化/自然/複合）の導出を行う。
"""

from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path
from typing import NamedTuple
from urllib.parse import unquote

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.data_loader import OPTIONAL_COLUMNS, REQUIRED_COLUMNS

LOGGER = logging.getLogger(__name__)

RAW_PATH: Path = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "raw"
    / "wikidata_world_heritage_sites.json"
)
OUTPUT_PATH: Path = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "heritage_sites.parquet"
)

_BARE_ID_RE = re.compile(r"^\d+$")
_LEADING_DIGITS_RE = re.compile(r"^(\d+)")
_COORD_RE = re.compile(r"^Point\(([-0-9.]+)\s+([-0-9.]+)\)$")
# P18 の値は http://commons.wikimedia.org/wiki/Special:FilePath/<ファイル名> 形式。
_FILEPATH_RE = re.compile(r"/Special:FilePath/(.+)$")

# UNESCOの分類基準そのもの: (i)〜(vi)は文化遺産基準、(vii)〜(x)は自然遺産基準。
_CRITERIA_ORDER: tuple[str, ...] = (
    "(i)",
    "(ii)",
    "(iii)",
    "(iv)",
    "(v)",
    "(vi)",
    "(vii)",
    "(viii)",
    "(ix)",
    "(x)",
)
_CULTURAL_CRITERIA = frozenset(_CRITERIA_ORDER[:6])
_NATURAL_CRITERIA = frozenset(_CRITERIA_ORDER[6:])


# 世界遺産条約に基づく最初の登録は1978年（それ以前の年はWikidataの誤記載か、
# 施設自体の設立年など無関係な日付が P580（開始時点）に誤って入力されたもの）。
_FIRST_INSCRIPTION_YEAR = 1978


class _ItemRecord:
    """Wikidata項目（QID）1件分の集約結果。"""

    def __init__(self) -> None:
        self.whc_id_raw: str | None = None
        self.name: str | None = None
        self.latitude: float | None = None
        self.longitude: float | None = None
        self.years: set[int] = set()
        self.countries: set[tuple[str, str]] = set()
        self.criteria: set[str] = set()
        self.image_filename: str | None = None


def _qid_from_uri(uri: str) -> str:
    return uri.rsplit("/", 1)[-1]


def _filename_from_image_uri(uri: str) -> str | None:
    """P18 の Commons URI から Wikimedia Commons のファイル名を取り出す。"""
    match = _FILEPATH_RE.search(uri)
    if not match:
        return None
    return unquote(match.group(1))


def _parse_coord(wkt: str) -> tuple[float, float] | None:
    """WKTの `Point(経度 緯度)` を (緯度, 経度) に変換する。"""
    match = _COORD_RE.match(wkt)
    if not match:
        return None
    lng, lat = float(match.group(1)), float(match.group(2))
    return lat, lng


def _aggregate_by_item(raw_bindings: list[dict]) -> dict[str, _ItemRecord]:
    """SPARQL束縛データをWikidata項目（QID）ごとに集約する。"""
    items: dict[str, _ItemRecord] = {}
    skipped_no_id = 0

    for row in raw_bindings:
        item_uri = row.get("item", {}).get("value")
        whc_id = row.get("whcId", {}).get("value")
        if not item_uri or not whc_id:
            skipped_no_id += 1
            continue

        qid = _qid_from_uri(item_uri)
        record = items.setdefault(qid, _ItemRecord())
        if record.whc_id_raw is None:
            record.whc_id_raw = whc_id
        if record.name is None:
            label = row.get("itemLabel", {}).get("value")
            if label:
                record.name = label

        if record.latitude is None:
            coord = row.get("coord", {}).get("value")
            if coord:
                parsed = _parse_coord(coord)
                if parsed:
                    record.latitude, record.longitude = parsed

        if record.image_filename is None:
            image_uri = row.get("image", {}).get("value")
            if image_uri:
                record.image_filename = _filename_from_image_uri(image_uri)

        date_raw = row.get("inscribedDate", {}).get("value")
        if date_raw:
            record.years.add(int(date_raw[:4]))

        iso_code = row.get("isoCode", {}).get("value", "")
        country_label = row.get("countryLabel", {}).get("value")
        if country_label:
            record.countries.add((iso_code, country_label))

        criteria_label = row.get("criteriaLabel", {}).get("value")
        if criteria_label:
            record.criteria.add(criteria_label)

    if skipped_no_id:
        LOGGER.info("WHC参照番号が無いため除外した束縛行: %d 行", skipped_no_id)

    return items


def _canonical_id(whc_id_raw: str) -> str | None:
    match = _LEADING_DIGITS_RE.match(whc_id_raw)
    return match.group(1) if match else None


def _ordered_group_qids(
    qids: list[str], items: dict[str, _ItemRecord]
) -> tuple[list[str], bool]:
    """グループ内のQIDを「代表候補を優先」した順に並べる。

    枝番なしID（例: "1200"）を持つアイテムを、その本体を表す代表アイテムとみなし
    先頭に置く。単一項目に全情報がまとまっているとは限らない（座標は代表に、
    登録基準は構成資産側にしか付与されていない、等のケースがWikidataには実在する）
    ため、名称は代表アイテムを優先しつつ、座標・登録年・国・登録基準はグループ内の
    全アイテムから欠損分を補い合う（fallback運用）。

    戻り値の bool は、枝番なしIDがグループ内に存在せずフォールバックしたかどうか。
    """
    bare_matches = sorted(
        qid for qid in qids if _BARE_ID_RE.match(items[qid].whc_id_raw or "")
    )
    if bare_matches:
        if len(bare_matches) > 1:
            LOGGER.warning("同一グループに枝番なしIDが複数存在します: %s", bare_matches)
        others = sorted(qid for qid in qids if qid not in bare_matches)
        return [*bare_matches, *others], False
    return sorted(qids), True


class _MergedSite(NamedTuple):
    """グループ（遺産1件）を統合した結果。"""

    name: str | None
    latitude: float | None
    longitude: float | None
    year: int | None
    countries: set[tuple[str, str]]
    criteria: set[str]
    wikidata_qid: str | None
    image_filename: str | None


def _merge_group(qids: list[str], items: dict[str, _ItemRecord]) -> _MergedSite:
    """代表アイテムを優先しつつ、グループ内の全アイテムから欠損項目を補って統合する。

    国・登録基準・登録年の候補はグループ全体の和集合を取る（複合遺産の構成資産側にしか
    タグ付けされていない場合があるため）。名称・座標・画像は先頭（代表）から順に見て
    最初に見つかった非欠損値を採用する。登録年は候補の中から1978年（世界遺産条約に
    基づく最初の登録年）以降の最小値を採る（Wikidataの誤記載による無関係な日付を除外
    するため）。1978年以降の候補が一つも無ければ欠損として扱う。

    ``wikidata_qid`` は先頭（代表）アイテムの QID。Commons ファイルページへの
    リンクやデバッグ用に保持する。
    """
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    image_filename: str | None = None
    years: set[int] = set()
    countries: set[tuple[str, str]] = set()
    criteria: set[str] = set()

    for qid in qids:
        record = items[qid]
        if name is None and record.name is not None:
            name = record.name
        if latitude is None and record.latitude is not None:
            latitude = record.latitude
            longitude = record.longitude
        if image_filename is None and record.image_filename is not None:
            image_filename = record.image_filename
        years |= record.years
        countries |= record.countries
        criteria |= record.criteria

    plausible_years = {y for y in years if y >= _FIRST_INSCRIPTION_YEAR}
    year = min(plausible_years) if plausible_years else None
    if years and year is None:
        LOGGER.warning(
            "登録年の候補が全て%d年より前でした（除外）: %s",
            _FIRST_INSCRIPTION_YEAR,
            sorted(years),
        )

    representative_qid = qids[0] if qids else None
    return _MergedSite(
        name,
        latitude,
        longitude,
        year,
        countries,
        criteria,
        representative_qid,
        image_filename,
    )


def _derive_category(criteria: set[str]) -> str | None:
    if not criteria:
        return None
    is_cultural = bool(criteria & _CULTURAL_CRITERIA)
    is_natural = bool(criteria & _NATURAL_CRITERIA)
    if is_cultural and is_natural:
        return "Mixed"
    if is_cultural:
        return "Cultural"
    if is_natural:
        return "Natural"
    return None


def _sorted_criteria_string(criteria: set[str]) -> str:
    known = [c for c in _CRITERIA_ORDER if c in criteria]
    unknown = sorted(criteria - set(_CRITERIA_ORDER))
    if unknown:
        LOGGER.warning("未知の登録基準表記です: %s", unknown)
    return "".join(known + unknown)


def _select_country(countries: set[tuple[str, str]]) -> tuple[str, str]:
    """越境遺産の場合、ISOコード昇順（欠損は末尾）で先頭の国を採用する。"""
    return min(countries, key=lambda c: (c[0] or "zz", c[1]))


def build_dataframe(raw_bindings: list[dict]) -> pd.DataFrame:
    """SPARQL束縛データから遺産単位のDataFrameを構築する。

    Args:
        raw_bindings: `results.bindings` の中身（辞書のリスト）。

    Returns:
        `REQUIRED_COLUMNS` + `OPTIONAL_COLUMNS` の列を持つDataFrame。
    """
    items = _aggregate_by_item(raw_bindings)

    groups: dict[str, list[str]] = {}
    for qid, record in items.items():
        if not record.whc_id_raw:
            continue
        canonical = _canonical_id(record.whc_id_raw)
        if canonical is None:
            continue
        groups.setdefault(canonical, []).append(qid)

    rows: list[dict] = []
    fallback_count = 0
    dropped_count = 0

    for canonical_id, qids in groups.items():
        ordered_qids, used_fallback = _ordered_group_qids(qids, items)
        if used_fallback:
            fallback_count += 1

        merged = _merge_group(ordered_qids, items)
        name = merged.name
        latitude = merged.latitude
        longitude = merged.longitude
        year = merged.year
        countries = merged.countries
        criteria = merged.criteria

        category = _derive_category(criteria)
        if (
            category is None
            or latitude is None
            or longitude is None
            or year is None
            or name is None
            or not countries
        ):
            dropped_count += 1
            continue

        iso_code, country_label = _select_country(countries)
        rows.append(
            {
                "site_id": int(canonical_id),
                "name": name,
                "country": country_label,
                "iso_code": iso_code,
                "category": category,
                "date_inscribed": year,
                "latitude": latitude,
                "longitude": longitude,
                "criteria": _sorted_criteria_string(criteria),
                "wikidata_qid": merged.wikidata_qid or "",
                "image_filename": merged.image_filename or "",
            }
        )

    LOGGER.info(
        "遺産件数: %d（フォールバック代表選択: %d件, 欠損により除外: %d件）",
        len(rows),
        fallback_count,
        dropped_count,
    )

    columns = [*REQUIRED_COLUMNS, *OPTIONAL_COLUMNS]
    df = pd.DataFrame(rows, columns=columns)
    return df.sort_values("site_id").reset_index(drop=True)


def load_raw_bindings(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload["results"]["bindings"]


def main() -> None:
    raw_bindings = load_raw_bindings(RAW_PATH)
    LOGGER.info("生データを読み込みました: %s（%d行）", RAW_PATH, len(raw_bindings))
    df = build_dataframe(raw_bindings)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_PATH, index=False)
    LOGGER.info("保存しました: %s", OUTPUT_PATH)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    try:
        main()
    except Exception:
        LOGGER.exception("データセットの構築に失敗しました。")
        sys.exit(1)
