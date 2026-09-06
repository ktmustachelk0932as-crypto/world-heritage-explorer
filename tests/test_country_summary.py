"""app.components.country_summary のユニットテスト。"""

from __future__ import annotations

from streamlit.testing.v1 import AppTest

_SCRIPT = """
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

import pandas as pd

from app.components.country_summary import (
    render_country_bar_chart,
    render_country_detail,
)
from core.aggregations import summarize_by_country
from core.data_loader import REQUIRED_COLUMNS

sites = pd.DataFrame(
    [
        (661, "Himeji-jo", "Japan", "JP", "Cultural", 1993, 34.8, 134.7),
        (662, "Yakushima", "Japan", "JP", "Natural", 1993, 30.4, 130.5),
        (664, "Test Mixed", "Japan", "JP", "Mixed", 2000, 35.0, 135.0),
        (3, "Aachen Cathedral", "Germany", "DE", "Cultural", 1978, 50.8, 6.1),
    ],
    columns=list(REQUIRED_COLUMNS),
)
summary = summarize_by_country(sites)

render_country_bar_chart(summary, top_n=10)
render_country_detail(sites, summary, "Japan")
"""

_EMPTY_SCRIPT = """
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from core.aggregations import summarize_by_country
from core.data_loader import REQUIRED_COLUMNS
from app.components.country_summary import render_country_bar_chart

import pandas as pd

empty = pd.DataFrame(columns=list(REQUIRED_COLUMNS))
render_country_bar_chart(summarize_by_country(empty), top_n=10)
"""


def test_country_summary_renders_without_exception() -> None:
    at = AppTest.from_string(_SCRIPT).run()
    assert not at.exception


def test_country_detail_shows_metrics_and_sites() -> None:
    at = AppTest.from_string(_SCRIPT).run()
    assert not at.exception
    subheaders = " ".join(s.value for s in at.subheader)
    assert "Japan" in subheaders
    metrics = {m.label: m.value for m in at.metric}
    assert metrics["登録件数"] == "3"  # Japan の登録件数合計（3件）
    assert metrics["自然遺産"] == "1"


def test_bar_chart_handles_empty_summary() -> None:
    at = AppTest.from_string(_EMPTY_SCRIPT).run()
    assert not at.exception
    assert any("データがありません" in info.value for info in at.info)
