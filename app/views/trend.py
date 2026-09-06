"""登録推移ページ：年次の世界遺産登録数を折れ線・エリアチャートで表示する（全世界／国別切替）。"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import streamlit as st

from app.components.trend_chart import render_trend_chart
from core.aggregations import summarize_by_country, yearly_counts
from core.data_loader import PARQUET_PATH, SAMPLE_CSV_PATH, load_heritage_sites

_SCOPE_WORLD = "全世界"
_SCOPE_COUNTRY = "国別"


@st.cache_data(show_spinner=False)
def _load_sites() -> pd.DataFrame:
    return load_heritage_sites()


@st.cache_data(show_spinner=False)
def _country_options() -> list[str]:
    return summarize_by_country(_load_sites())["country"].tolist()


@st.cache_data(show_spinner=False)
def _yearly(country: str | None) -> pd.DataFrame:
    """累積の年次推移（分類内訳付き）。表示は常に累積なので cumulative 固定。"""
    return yearly_counts(_load_sites(), country=country, cumulative=True)


st.title("世界遺産の登録数推移")

try:
    sites = _load_sites()
except (FileNotFoundError, ValueError) as exc:
    st.error(f"データの読み込みに失敗しました: {exc}")
    st.stop()

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

# 表示は常に累積・分類内訳あり。
render_trend_chart(yearly, cumulative=True, show_breakdown=True)

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
        "- 登録年は初回登録年のみを集計しており、後年の登録範囲の拡張・変更は反映していません\n"
        "- 複数国にまたがる遺産（越境遺産）は代表1か国のみで集計しています\n"
        "- 分類（文化遺産/自然遺産/複合遺産）はWikidataの情報を基に算出しており、"
        "UNESCO公式データと差異がある場合があります"
    )
