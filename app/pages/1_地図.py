"""インタラクティブ地図ページ：世界遺産をマーカー表示し、クリックで詳細情報を表示する。"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
from streamlit_folium import st_folium

from app.components.detail_panel import render_detail_panel
from app.components.map_view import (
    CATEGORY_LABELS_JA,
    CATEGORY_MARKER_COLORS,
    build_map,
    find_site_by_coordinates,
)
from core.data_loader import PARQUET_PATH, SAMPLE_CSV_PATH, load_heritage_sites

_SELECTED_KEY = "selected_site_id"

st.set_page_config(page_title="地図", page_icon="🗺️", layout="wide")
st.title("世界遺産マップ")

try:
    sites = load_heritage_sites()
except (FileNotFoundError, ValueError) as exc:
    st.error(f"データの読み込みに失敗しました: {exc}")
    st.stop()

map_col, detail_col = st.columns([2, 1], gap="large")

with map_col:
    legend = "　".join(
        f"<span style='color:{CATEGORY_MARKER_COLORS[key]}'>●</span> {label}"
        for key, label in CATEGORY_LABELS_JA.items()
    )
    st.markdown(legend, unsafe_allow_html=True)

    source_path = PARQUET_PATH if PARQUET_PATH.exists() else SAMPLE_CSV_PATH
    fetched_at = (
        datetime.fromtimestamp(source_path.stat().st_mtime, tz=UTC)
        .astimezone()
        .strftime("%Y-%m-%d")
    )
    st.caption(f"{len(sites)} 件を表示（データ取得日: {fetched_at}）")
    with st.expander("※ データについての注記"):
        st.markdown(
            "- 実際の世界遺産登録数と完全には一致しない場合があります"
            "（データ取得元の制約により一部の遺産が含まれていません）\n"
            "- 複数地点にまたがる遺産は代表1地点の座標で表示しています\n"
            "- 複数国にまたがる遺産（越境遺産）は代表1か国のみを表示しています\n"
            "- 登録年は初回登録年のみを表示しており、後年の登録範囲の拡張・変更は反映していません\n"
            "- 座標・分類（文化遺産/自然遺産/複合遺産）はWikidataの情報を基に算出しており、"
            "UNESCO公式データと差異がある場合があります"
        )

    map_state = st_folium(
        build_map(sites),
        use_container_width=True,
        height=650,
        returned_objects=["last_object_clicked"],
    )

clicked = (map_state or {}).get("last_object_clicked")
if clicked:
    site = find_site_by_coordinates(sites, clicked["lat"], clicked["lng"])
    if site is not None:
        st.session_state[_SELECTED_KEY] = int(site["site_id"])

selected_id = st.session_state.get(_SELECTED_KEY)
selected_rows = (
    sites[sites["site_id"] == selected_id]
    if selected_id is not None
    else sites.iloc[0:0]
)
selected = selected_rows.iloc[0] if not selected_rows.empty else None

with detail_col:
    render_detail_panel(selected)
    if selected is not None and st.button("選択をクリア"):
        del st.session_state[_SELECTED_KEY]
        st.rerun()
