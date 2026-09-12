"""app/views/map.py（地図ページ）の検索フォーカス処理のユニットテスト。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from core.data_loader import load_heritage_sites

_MAIN = str(Path(__file__).resolve().parents[1] / "app" / "main.py")
_SEARCH_KEY = "map_site_search"
_FOCUS_KEY = "map_focus_center"
_FOCUS_SEQ_KEY = "map_focus_seq"


def _coords(sites: pd.DataFrame, site_id: int) -> list[float]:
    row = sites.loc[sites["site_id"] == site_id].iloc[0]
    return [float(row["latitude"]), float(row["longitude"])]


def test_each_search_moves_focus_and_bumps_map_key() -> None:
    sites = load_heritage_sites()
    first, second = (int(v) for v in sites["site_id"].iloc[:2])

    at = AppTest.from_file(_MAIN, default_timeout=60).run()
    assert not at.exception
    assert _FOCUS_SEQ_KEY not in at.session_state

    at.selectbox(key=_SEARCH_KEY).select(first).run()
    assert not at.exception
    assert at.session_state[_FOCUS_KEY] == _coords(sites, first)
    assert at.session_state[_FOCUS_SEQ_KEY] == 1

    # 2 回目の検索でも連番が進み、地図コンポーネントが作り直される
    at.selectbox(key=_SEARCH_KEY).select(second).run()
    assert not at.exception
    assert at.session_state[_FOCUS_KEY] == _coords(sites, second)
    assert at.session_state[_FOCUS_SEQ_KEY] == 2

    # 検索値が変わらない再実行では連番は進まない
    at.run()
    assert at.session_state[_FOCUS_SEQ_KEY] == 2
