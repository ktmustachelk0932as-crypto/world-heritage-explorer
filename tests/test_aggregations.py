"""core.aggregations のユニットテスト。"""

from __future__ import annotations

import pandas as pd

from core.aggregations import (
    COUNTRY_SUMMARY_COLUMNS,
    count_by_category,
    summarize_by_country,
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
