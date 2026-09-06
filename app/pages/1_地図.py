"""インタラクティブ地図ページ：世界遺産をマーカー表示し、クリックで詳細情報を表示する。"""

from __future__ import annotations

import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from app.components.detail_panel import render_detail_panel
from app.components.map_view import (
    CATEGORY_LABELS_JA,
    CATEGORY_MARKER_COLORS,
    build_map,
    find_site_by_coordinates,
)
from core.data_loader import (
    PARQUET_PATH,
    SAMPLE_CSV_PATH,
    load_heritage_images,
    load_heritage_sites,
)
from core.env import load_env_file
from core.image_fetcher import fetch_commons_image_info

_SELECTED_KEY = "selected_site_id"

# フォールバック取得の User-Agent 用に、.env / secrets の連絡先を環境変数へ渡す。
load_env_file()
# secrets.toml が無い環境では st.secrets へのアクセス自体が例外になるため握りつぶす。
try:
    _contact = str(st.secrets.get("WIKIMEDIA_CONTACT_EMAIL", "") or "")
except Exception:  # noqa: BLE001 - secrets 未設定は正常系として無視する
    _contact = ""
if _contact:
    os.environ.setdefault("WIKIMEDIA_CONTACT_EMAIL", _contact)


@st.cache_data(ttl=timedelta(days=30), show_spinner=False)
def _load_images() -> pd.DataFrame:
    """事前取得済み画像スナップショット（無ければ空 DataFrame）。"""
    return load_heritage_images()


@st.cache_data(ttl=timedelta(days=7), show_spinner=False)
def _fallback_image(filename: str) -> dict | None:
    """スナップショットに無い遺産の画像をランタイムで単発取得する（計画書11.2）。"""
    if not filename:
        return None
    # fetch_commons_image_info は失敗しても例外を送出せず status で返す（計画書11.4）。
    info = fetch_commons_image_info(filename)
    if info.status != "ok":
        return None
    return {
        "image_url": info.image_url,
        "source_page_url": info.source_page_url,
        "license_short_name": info.license_short_name,
        "license_url": info.license_url,
        "artist": info.artist,
        "attribution_required": info.attribution_required,
    }


def _image_for(site: pd.Series, images: pd.DataFrame) -> object | None:
    """選択遺産の画像情報を返す（スナップショット優先、無ければフォールバック取得）。"""
    hit = images[images["site_id"] == int(site["site_id"])]
    if not hit.empty:
        return hit.iloc[0]
    return _fallback_image(str(site.get("image_filename", "") or ""))


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
    image = _image_for(selected, _load_images()) if selected is not None else None
    render_detail_panel(selected, image)
    if selected is not None and st.button("選択をクリア"):
        del st.session_state[_SELECTED_KEY]
        st.rerun()
