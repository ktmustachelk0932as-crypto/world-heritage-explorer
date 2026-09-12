"""登録推移ページ：年次の世界遺産登録数を積み上げエリアチャートで表示する（全世界／国別切替）。"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.components.page_common import (
    load_sites_cached,
    load_sites_or_stop,
    render_data_notes,
)
from app.components.trend_chart import render_trend_chart
from core.aggregations import summarize_by_country, yearly_counts
from core.data_loader import data_fetched_date

_SCOPE_WORLD = "全世界"
_SCOPE_COUNTRY = "国別"

_DATA_NOTES = (
    (
        "実際の世界遺産登録数と完全には一致しない場合があります"
        "（データ取得元の制約により一部の遺産が含まれていません）"
    ),
    "登録年は初回登録年のみを集計しており、後年の登録範囲の拡張・変更は反映していません",
    "複数国にまたがる遺産（越境遺産）は代表1か国のみで集計しています",
    (
        "分類（文化遺産/自然遺産/複合遺産）はWikidataの情報を基に算出しており、"
        "UNESCO公式データと差異がある場合があります"
    ),
)


@st.cache_data(show_spinner=False)
def _country_options() -> list[str]:
    return summarize_by_country(load_sites_cached())["country"].tolist()


@st.cache_data(show_spinner=False)
def _yearly(country: str | None) -> pd.DataFrame:
    """累積の年次推移（分類内訳付き）。表示は常に累積なので cumulative 固定。"""
    return yearly_counts(load_sites_cached(), country=country, cumulative=True)


st.title("世界遺産の登録数推移")

load_sites_or_stop()

scope = st.radio("集計対象", (_SCOPE_WORLD, _SCOPE_COUNTRY), horizontal=True)

country: str | None = None
if scope == _SCOPE_COUNTRY:
    options = _country_options()
    stored = st.session_state.get("selected_country")
    index = options.index(stored) if stored in options else 0
    country = st.selectbox("国 / 地域を選択", options, index=index)
    st.session_state["selected_country"] = country

yearly = _yearly(country)

if not yearly.empty:
    first_year = int(yearly["year"].iloc[0])
    last_year = int(yearly["year"].iloc[-1])
    metric_cols = st.columns(2)
    metric_cols[0].metric("対象期間", f"{first_year}–{last_year}")
    metric_cols[1].metric("登録件数（累積）", int(yearly["total"].iloc[-1]))

render_trend_chart(yearly)

st.caption(f"データ取得日: {data_fetched_date()}")
render_data_notes(_DATA_NOTES)
