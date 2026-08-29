"""インタラクティブ地図ページ：世界遺産をマーカー表示し、クリックで詳細情報を表示する。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
from streamlit_folium import st_folium

from app.components.map_view import (
    CATEGORY_LABELS_JA,
    CATEGORY_MARKER_COLORS,
    build_map,
)
from core.data_loader import load_heritage_sites

st.set_page_config(page_title="地図", page_icon="🗺️", layout="wide")
st.title("世界遺産マップ")

try:
    sites = load_heritage_sites()
except (FileNotFoundError, ValueError) as exc:
    st.error(f"データの読み込みに失敗しました: {exc}")
    st.stop()

legend = "　".join(
    f"<span style='color:{CATEGORY_MARKER_COLORS[key]}'>●</span> {label}"
    for key, label in CATEGORY_LABELS_JA.items()
)
st.markdown(legend, unsafe_allow_html=True)
st.caption(f"{len(sites)} 件を表示")

st_folium(
    build_map(sites),
    use_container_width=True,
    height=650,
    returned_objects=[],
)
