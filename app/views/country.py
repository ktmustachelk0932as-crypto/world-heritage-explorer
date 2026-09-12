"""国別サマリーページ：国ごとの登録件数・分類内訳をグラフ表示する。"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.components.country_summary import (
    render_country_bar_chart,
    render_country_detail,
)
from app.components.map_view import CATEGORY_LABELS_JA
from app.components.page_common import (
    load_sites_cached,
    load_sites_or_stop,
    render_data_notes,
)
from core.aggregations import CATEGORY_KEYS, count_by_category, summarize_by_country
from core.data_loader import data_fetched_date

_SELECTED_COUNTRY_KEY = "selected_country"

_DATA_NOTES = (
    (
        "実際の世界遺産登録数と完全には一致しない場合があります"
        "（データ取得元の制約により一部の遺産が含まれていません）"
    ),
    "複数国にまたがる遺産（越境遺産）は代表1か国のみで集計しています",
    (
        "分類（文化遺産/自然遺産/複合遺産）はWikidataの情報を基に算出しており、"
        "UNESCO公式データと差異がある場合があります"
    ),
)


@st.cache_data(show_spinner=False)
def _summary() -> pd.DataFrame:
    return summarize_by_country(load_sites_cached())


st.title("国別サマリー")

sites = load_sites_or_stop()
summary = _summary()

by_category = count_by_category(sites)
metric_cols = st.columns(5)
metric_cols[0].metric("対象国 / 地域数", len(summary))
metric_cols[1].metric("登録件数（合計）", len(sites))
for col, key in zip(metric_cols[2:], CATEGORY_KEYS, strict=True):
    col.metric(CATEGORY_LABELS_JA[key], by_category[key])

st.caption(f"データ取得日: {data_fetched_date()}")
render_data_notes(_DATA_NOTES)

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
