"""各ページで共通するデータ読み込み・注記表示（Streamlit 依存）。"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd
import streamlit as st

from core.data_loader import load_heritage_sites


@st.cache_data(show_spinner=False)
def load_sites_cached() -> pd.DataFrame:
    """世界遺産サイト一覧（ページ再実行・ページ遷移をまたいでキャッシュ）。"""
    return load_heritage_sites()


def load_sites_or_stop() -> pd.DataFrame:
    """サイト一覧を返す。読み込みに失敗したらエラー表示してページを止める。"""
    try:
        return load_sites_cached()
    except (FileNotFoundError, ValueError) as exc:
        st.error(f"データの読み込みに失敗しました: {exc}")
        st.stop()


def render_data_notes(notes: Sequence[str]) -> None:
    """「データについての注記」を折りたたみで表示する。"""
    with st.expander("※ データについての注記"):
        st.markdown("\n".join(f"- {note}" for note in notes))
