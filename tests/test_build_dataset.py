"""scripts.build_dataset のユニットテスト。"""

from __future__ import annotations

from core.data_loader import ALLOWED_CATEGORIES, OPTIONAL_COLUMNS, REQUIRED_COLUMNS
from scripts.build_dataset import build_dataframe


def _binding(
    item: str,
    item_label: str,
    whc_id: str,
    *,
    coord: str | None = None,
    year: int | None = None,
    country_qid: str | None = None,
    country_label: str | None = None,
    iso: str | None = None,
    criteria: str | None = None,
    image: str | None = None,
) -> dict:
    """SPARQL結果JSONの束縛（binding）1行分を模した辞書を組み立てる。"""
    row: dict = {
        "item": {"value": f"http://www.wikidata.org/entity/{item}"},
        "itemLabel": {"value": item_label},
        "whcId": {"value": whc_id},
    }
    if coord is not None:
        row["coord"] = {"value": coord}
    if year is not None:
        row["inscribedDate"] = {"value": f"{year}-01-01T00:00:00Z"}
    if country_qid is not None:
        row["country"] = {"value": f"http://www.wikidata.org/entity/{country_qid}"}
    if country_label is not None:
        row["countryLabel"] = {"value": country_label}
    if iso is not None:
        row["isoCode"] = {"value": iso}
    if criteria is not None:
        row["criteriaLabel"] = {"value": criteria}
    if image is not None:
        row["image"] = {
            "value": f"http://commons.wikimedia.org/wiki/Special:FilePath/{image}"
        }
    return row


def test_single_country_mixed_criteria() -> None:
    """単一国・文化基準と自然基準の両方を持つ遺産はMixedになる。"""
    bindings = [
        _binding(
            "Q1",
            "Ngorongoro Conservation Area",
            "39",
            coord="Point(35.5 -3.2)",
            year=1979,
            country_qid="Q924",
            country_label="United Republic of Tanzania",
            iso="TZ",
            criteria=c,
        )
        for c in ("(iv)", "(vii)", "(viii)", "(ix)", "(x)")
    ]

    df = build_dataframe(bindings)

    assert set(REQUIRED_COLUMNS).issubset(df.columns)
    assert "criteria" in df.columns
    row = df.loc[df["site_id"] == 39].iloc[0]
    assert row["category"] == "Mixed"
    assert row["criteria"] == "(iv)(vii)(viii)(ix)(x)"
    assert row["iso_code"] == "TZ"


def test_component_sites_are_deduplicated_and_merged() -> None:
    """枝番付きIDを持つ構成資産は1件に重複排除され、名称・座標は代表アイテム
    （枝番なしID）から、国・登録基準は構成資産側の値も合わせて統合される。

    Wikidataでは座標が代表アイテムに、登録基準が構成資産側にしか
    タグ付けされていないケースが実在するため、単純に代表アイテムの値のみを
    採用すると多くの遺産が欠損扱いで脱落してしまう。そのためグループ全体から
    値を補い合う設計にしている。
    """
    bindings = [
        _binding(
            "Q10",
            "Main Site",
            "1200",
            coord="Point(10.0 20.0)",
            year=2000,
            country_qid="Q1",
            country_label="Country A",
            iso="AA",
            criteria="(i)",
            image="Main_Site.jpg",
        ),
        _binding(
            "Q10",
            "Main Site",
            "1200",
            coord="Point(10.0 20.0)",
            year=2000,
            country_qid="Q1",
            country_label="Country A",
            iso="AA",
            criteria="(ii)",
        ),
        _binding(
            "Q11",
            "Component of Main Site",
            "1200-001",
            coord="Point(11.0 21.0)",
            year=2000,
            country_qid="Q2",
            country_label="Country B",
            iso="BB",
            criteria="(iii)",
            image="Component.jpg",
        ),
    ]

    df = build_dataframe(bindings)

    matched = df.loc[df["site_id"] == 1200]
    assert len(matched) == 1
    row = matched.iloc[0]
    # 名称・座標・画像・代表QIDは代表アイテム（枝番なしID="1200"のQ10）のもの。
    assert row["name"] == "Main Site"
    assert row["latitude"] == 20.0
    assert row["longitude"] == 10.0
    assert row["wikidata_qid"] == "Q10"
    assert row["image_filename"] == "Main_Site.jpg"
    # 国はグループ全体（Country A, Country B）のうちISOコード昇順で先頭。
    assert row["country"] == "Country A"
    assert row["iso_code"] == "AA"
    # 登録基準は構成資産側の (iii) も合わせて統合される。
    assert row["category"] == "Cultural"
    assert row["criteria"] == "(i)(ii)(iii)"


def test_missing_coordinate_on_representative_is_filled_from_component() -> None:
    """代表アイテムに座標が無い場合、構成資産側の座標で補われる。"""
    bindings = [
        _binding(
            "Q50",
            "Main Site",
            "1600",
            year=1995,
            country_qid="Q1",
            country_label="Country A",
            iso="AA",
            criteria="(vii)",
        ),
        _binding(
            "Q51",
            "Component of Main Site",
            "1600-001",
            coord="Point(9.0 9.0)",
        ),
    ]

    df = build_dataframe(bindings)

    matched = df.loc[df["site_id"] == 1600]
    assert len(matched) == 1
    assert matched.iloc[0]["latitude"] == 9.0
    assert matched.iloc[0]["longitude"] == 9.0


def test_transboundary_site_picks_first_iso_alphabetically() -> None:
    """越境遺産は複数国を持つが、ISOコード昇順で先頭の国を採用する。"""
    bindings = [
        _binding(
            "Q20",
            "Wadden Sea",
            "1314",
            coord="Point(8.0 53.5)",
            year=2009,
            country_qid="Q183",
            country_label="Germany",
            iso="DE",
            criteria="(vii)",
        ),
        _binding(
            "Q20",
            "Wadden Sea",
            "1314",
            coord="Point(8.0 53.5)",
            year=2009,
            country_qid="Q29999",
            country_label="Netherlands",
            iso="NL",
            criteria="(viii)",
        ),
    ]

    df = build_dataframe(bindings)

    row = df.loc[df["site_id"] == 1314].iloc[0]
    assert row["category"] == "Natural"
    assert row["iso_code"] == "DE"
    assert row["country"] == "Germany"


def test_all_cultural_criteria() -> None:
    """(i)〜(vi) の基準のみを持つ遺産はCulturalになる。"""
    bindings = [
        _binding(
            "Q30",
            "Historic City",
            "500",
            coord="Point(1.0 1.0)",
            year=1990,
            country_qid="Q1",
            country_label="Country A",
            iso="AA",
            criteria=c,
        )
        for c in ("(ii)", "(iv)")
    ]

    df = build_dataframe(bindings)

    row = df.loc[df["site_id"] == 500].iloc[0]
    assert row["category"] == "Cultural"


def test_representative_fallback_when_no_bare_id_exists() -> None:
    """枝番なしIDが存在しないグループでも、QID最小のアイテムを名称・座標の
    代表として採用しつつ、登録基準はグループ全体から統合して1行生成する。
    """
    bindings = [
        _binding(
            "Q41",
            "Component 1",
            "1400-001",
            coord="Point(2.0 2.0)",
            year=1985,
            country_qid="Q1",
            country_label="Country A",
            iso="AA",
            criteria="(vii)",
            image="Component_1.jpg",
        ),
        _binding(
            "Q40",
            "Component 2",
            "1400-002",
            coord="Point(3.0 3.0)",
            year=1985,
            country_qid="Q1",
            country_label="Country A",
            iso="AA",
            criteria="(viii)",
        ),
    ]

    df = build_dataframe(bindings)

    matched = df.loc[df["site_id"] == 1400]
    assert len(matched) == 1
    row = matched.iloc[0]
    # QID最小（Q40）が名称・座標・代表QIDとして選ばれる。
    assert row["name"] == "Component 2"
    assert row["latitude"] == 3.0
    assert row["wikidata_qid"] == "Q40"
    # 代表（Q40）に画像が無いので、グループ内の Q41 の画像で補われる。
    assert row["image_filename"] == "Component_1.jpg"
    # 登録基準はグループ全体（(vii)と(viii)）を統合する。
    assert row["criteria"] == "(vii)(viii)"
    assert row["category"] == "Natural"


def test_image_filename_from_p18_is_url_decoded() -> None:
    """P18（Special:FilePath 形式）から取り出すファイル名は URL デコードされる。"""
    bindings = [
        _binding(
            "Q70",
            "Aachen Cathedral",
            "3",
            coord="Point(6.08 50.77)",
            year=1978,
            country_qid="Q183",
            country_label="Germany",
            iso="DE",
            criteria="(i)",
            image="Aachen%20Cathedral%20-%20interior.jpg",
        ),
    ]

    df = build_dataframe(bindings)

    row = df.loc[df["site_id"] == 3].iloc[0]
    assert row["image_filename"] == "Aachen Cathedral - interior.jpg"


def test_missing_p18_leaves_image_filename_empty_but_keeps_site() -> None:
    """P18 が無い遺産は image_filename が空文字になるだけで、除外はされない。"""
    bindings = [
        _binding(
            "Q80",
            "No Image Site",
            "800",
            coord="Point(1.0 1.0)",
            year=1990,
            country_qid="Q1",
            country_label="Country A",
            iso="AA",
            criteria="(ii)",
        ),
    ]

    df = build_dataframe(bindings)

    row = df.loc[df["site_id"] == 800].iloc[0]
    assert row["image_filename"] == ""
    assert row["wikidata_qid"] == "Q80"


def test_output_schema_and_categories() -> None:
    """出力DataFrameの列と分類が core.data_loader の契約を満たす。"""
    bindings = [
        _binding(
            "Q1",
            "Site",
            "1",
            coord="Point(1.0 1.0)",
            year=2000,
            country_qid="Q1",
            country_label="Country A",
            iso="AA",
            criteria="(i)",
        )
    ]

    df = build_dataframe(bindings)

    assert list(df.columns) == [*REQUIRED_COLUMNS, *OPTIONAL_COLUMNS]
    assert set(df["category"]).issubset(ALLOWED_CATEGORIES)


def test_implausible_pre_1978_date_is_ignored_in_favor_of_valid_candidate() -> None:
    """1978年（世界遺産条約に基づく最初の登録年）より前の日付は無視し、
    それ以降の候補があればそちらを採用する（実データで、施設の設立年など
    無関係な日付がP580に誤って入力されている例が確認されている）。
    """
    bindings = [
        _binding(
            "Q60",
            "Serengeti National Park",
            "156",
            coord="Point(35.0 -2.3)",
            year=1960,
            country_qid="Q924",
            country_label="Tanzania",
            iso="TZ",
            criteria="(vii)",
        ),
        _binding(
            "Q60",
            "Serengeti National Park",
            "156",
            coord="Point(35.0 -2.3)",
            year=1981,
            country_qid="Q924",
            country_label="Tanzania",
            iso="TZ",
            criteria="(x)",
        ),
    ]

    df = build_dataframe(bindings)

    row = df.loc[df["site_id"] == 156].iloc[0]
    assert row["date_inscribed"] == 1981


def test_all_candidate_dates_pre_1978_drops_the_site() -> None:
    """1978年より前の日付しか候補が無い場合は登録年が欠損とみなされ、
    その遺産は出力から除外される。
    """
    bindings = [
        _binding(
            "Q61",
            "Bogus Early Site",
            "9999",
            coord="Point(1.0 1.0)",
            year=1965,
            country_qid="Q1",
            country_label="Country A",
            iso="AA",
            criteria="(vii)",
        ),
    ]

    df = build_dataframe(bindings)

    assert df.loc[df["site_id"] == 9999].empty
