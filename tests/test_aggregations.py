"""core.aggregations のユニットテスト。"""

from __future__ import annotations

import pandas as pd

from core.aggregations import (
    COUNTRY_SUMMARY_COLUMNS,
    YEARLY_COUNTS_COLUMNS,
    count_by_category,
    summarize_by_country,
    yearly_counts,
)
from core.data_loader import REQUIRED_COLUMNS

_SAMPLE = pd.DataFrame(
    [
        (661, "Himeji-jo", "Japan", "JP", "Cultural", 1993, 34.8394, 134.6939),
        (662, "Yakushima", "Japan", "JP", "Natural", 1993, 30.3583, 130.5333),
        (663, "Shirakami", "Japan", "JP", "Natural", 1993, 40.4667, 140.0833),
        (664, "Test Mixed", "Japan", "JP", "Mixed", 2000, 35.0, 135.0),
        (3, "Aachen Cathedral", "Germany", "DE", "Cultural", 1978, 50.7745, 6.0839),
        (28, "Yellowstone", "United States", "US", "Natural", 1978, 44.428, -110.588),
    ],
    columns=list(REQUIRED_COLUMNS),
)


def test_summarize_by_country_columns_and_row_count() -> None:
    result = summarize_by_country(_SAMPLE)
    assert list(result.columns) == list(COUNTRY_SUMMARY_COLUMNS)
    assert len(result) == 3  # Japan / Germany / United States


def test_summarize_by_country_counts_and_breakdown() -> None:
    result = summarize_by_country(_SAMPLE).set_index("country")
    assert result.loc["Japan", "total"] == 4
    assert result.loc["Japan", "cultural"] == 1
    assert result.loc["Japan", "natural"] == 2
    assert result.loc["Japan", "mixed"] == 1
    assert result.loc["Japan", "iso_code"] == "JP"


def test_summarize_by_country_sorted_by_total_desc_then_name() -> None:
    df = pd.concat([_SAMPLE, _SAMPLE.assign(country="Germany", iso_code="DE")])
    result = summarize_by_country(df)
    # Germany が最多になり先頭。同数の Japan / United States は国名昇順。
    assert result.iloc[0]["country"] == "Germany"
    tail = result[result["country"] != "Germany"]["country"].tolist()
    assert tail == sorted(tail)


def test_summarize_by_country_empty_input() -> None:
    empty = _SAMPLE.iloc[0:0]
    result = summarize_by_country(empty)
    assert list(result.columns) == list(COUNTRY_SUMMARY_COLUMNS)
    assert result.empty


def test_count_by_category_has_all_keys() -> None:
    counts = count_by_category(_SAMPLE)
    assert counts == {"Cultural": 2, "Natural": 3, "Mixed": 1}


def test_count_by_category_zero_for_absent_category() -> None:
    cultural_only = _SAMPLE[_SAMPLE["category"] == "Cultural"]
    counts = count_by_category(cultural_only)
    assert counts == {"Cultural": 2, "Natural": 0, "Mixed": 0}


def test_yearly_counts_columns_and_fills_gap_years() -> None:
    result = yearly_counts(_SAMPLE)
    assert list(result.columns) == list(YEARLY_COUNTS_COLUMNS)
    # 1978〜2000 の全年が連続して並ぶ（登録のない年も 0 で埋める）。
    assert result["year"].tolist() == list(range(1978, 2001))
    assert (result["year"].diff().dropna() == 1).all()


def test_yearly_counts_values_and_breakdown() -> None:
    result = yearly_counts(_SAMPLE).set_index("year")
    assert result.loc[1978, "total"] == 2
    assert result.loc[1978, "cultural"] == 1
    assert result.loc[1978, "natural"] == 1
    assert result.loc[1993, "total"] == 3
    assert result.loc[1993, "natural"] == 2
    assert result.loc[1990, "total"] == 0  # 登録のない年


def test_yearly_counts_filters_by_country() -> None:
    result = yearly_counts(_SAMPLE, country="Japan").set_index("year")
    assert result["total"].sum() == 4
    assert result.index.min() == 1993
    assert result.loc[2000, "mixed"] == 1


def test_yearly_counts_cumulative_is_monotonic_and_reaches_total() -> None:
    result = yearly_counts(_SAMPLE, cumulative=True)
    assert result["total"].is_monotonic_increasing
    assert result["total"].iloc[-1] == len(_SAMPLE)
    assert result["total"].iloc[0] == 2  # 1978 の 2 件


def test_yearly_counts_empty_input() -> None:
    result = yearly_counts(_SAMPLE.iloc[0:0])
    assert list(result.columns) == list(YEARLY_COUNTS_COLUMNS)
    assert result.empty


def test_yearly_counts_unknown_country_returns_empty() -> None:
    result = yearly_counts(_SAMPLE, country="Atlantis")
    assert result.empty
