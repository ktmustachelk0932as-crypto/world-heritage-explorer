"""app.components.trend_chart のユニットテスト。"""

from __future__ import annotations

from streamlit.testing.v1 import AppTest

_SCRIPT = """
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

import pandas as pd

from app.components.trend_chart import render_trend_chart
from core.aggregations import yearly_counts
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

render_trend_chart(yearly_counts(sites, cumulative=True))
"""

_EMPTY_SCRIPT = """
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

import pandas as pd

from app.components.trend_chart import render_trend_chart
from core.aggregations import yearly_counts
from core.data_loader import REQUIRED_COLUMNS

empty = pd.DataFrame(columns=list(REQUIRED_COLUMNS))
render_trend_chart(yearly_counts(empty, cumulative=True))
"""


def test_trend_chart_renders_without_exception() -> None:
    at = AppTest.from_string(_SCRIPT).run()
    assert not at.exception


def test_trend_chart_handles_empty_yearly() -> None:
    at = AppTest.from_string(_EMPTY_SCRIPT).run()
    assert not at.exception
    assert any("データがありません" in info.value for info in at.info)
