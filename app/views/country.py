"""国別サマリーページ：国ごとの登録件数・分類内訳をグラフ表示する。"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import streamlit as st

from app.components.country_summary import (
    render_country_bar_chart,
    render_country_detail,
)
from app.components.map_view import CATEGORY_LABELS_JA
from core.aggregations import count_by_category, summarize_by_country
from core.data_loader import PARQUET_PATH, SAMPLE_CSV_PATH, load_heritage_sites

_SELECTED_COUNTRY_KEY = "selected_country"


@st.cache_data(show_spinner=False)
def _load_sites() -> pd.DataFrame:
    return load_heritage_sites()


@st.cache_data(show_spinner=False)
def _summary() -> pd.DataFrame:
    return summarize_by_country(_load_sites())


st.title("国別サマリー")

try:
    sites = _load_sites()
except (FileNotFoundError, ValueError) as exc:
    st.error(f"データの読み込みに失敗しました: {exc}")
    st.stop()

summary = _summary()

by_category = count_by_category(sites)
metric_cols = st.columns(5)
metric_cols[0].metric("対象国 / 地域数", len(summary))
metric_cols[1].metric("登録件数（合計）", len(sites))
metric_cols[2].metric(CATEGORY_LABELS_JA["Cultural"], by_category["Cultural"])
metric_cols[3].metric(CATEGORY_LABELS_JA["Natural"], by_category["Natural"])
metric_cols[4].metric(CATEGORY_LABELS_JA["Mixed"], by_category["Mixed"])

source_path = PARQUET_PATH if PARQUET_PATH.exists() else SAMPLE_CSV_PATH
fetched_at = (
    datetime.fromtimestamp(source_path.stat().st_mtime, tz=UTC)
    .astimezone()
    .strftime("%Y-%m-%d")
)
st.caption(f"データ取得日: {fetched_at}")
with st.expander("※ データについての注記"):
    st.markdown(
        "- 実際の世界遺産登録数と完全には一致しない場合があります"
        "（データ取得元の制約により一部の遺産が含まれていません）\n"
        "- 複数国にまたがる遺産（越境遺産）は代表1か国のみで集計しています\n"
        "- 分類（文化遺産/自然遺産/複合遺産）はWikidataの情報を基に算出しており、"
        "UNESCO公式データと差異がある場合があります"
    )

if summary.empty:
    st.info("表示できるデータがありません。")
    st.stop()

max_n = len(summary)
default_n = min(20, max_n)
top_n = (
    st.slider("表示する国数", min_value=5, max_value=max_n, value=default_n)
    if max_n > 5
    else max_n
)
render_country_bar_chart(summary, top_n=top_n)

st.divider()

countries = summary["country"].tolist()
stored = st.session_state.get(_SELECTED_COUNTRY_KEY)
index = countries.index(stored) if stored in countries else 0
country = st.selectbox("国 / 地域を選択", countries, index=index)
st.session_state[_SELECTED_COUNTRY_KEY] = country

render_country_detail(sites, summary, country)
