"""インタラクティブ地図ページ：世界遺産をマーカー表示し、クリック / 検索で詳細を表示する。"""

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
_LAST_CLICK_KEY = "map_last_handled_click"
_LAST_SEARCH_KEY = "map_last_handled_search"
_SEARCH_WIDGET_KEY = "map_site_search"
_CLEAR_FLAG_KEY = "map_clear_search"
_FOCUS_KEY = "map_focus_center"
_MAP_WIDGET_KEY = "heritage_map"
_FOCUS_ZOOM = 6

# フォールバック取得の User-Agent 用に、.env / secrets の連絡先を環境変数へ渡す。
load_env_file()
# secrets.toml が無い環境では st.secrets へのアクセス自体が例外になるため握りつぶす。
try:
    _contact = str(st.secrets.get("WIKIMEDIA_CONTACT_EMAIL", "") or "")
except Exception:  # noqa: BLE001 - secrets 未設定は正常系として無視する
    _contact = ""
if _contact:
    os.environ.setdefault("WIKIMEDIA_CONTACT_EMAIL", _contact)


@st.cache_data(show_spinner=False)
def _load_sites() -> pd.DataFrame:
    """世界遺産サイト一覧（ページ再実行・ページ遷移をまたいでキャッシュ）。"""
    return load_heritage_sites()


@st.cache_data(ttl=timedelta(days=30), show_spinner=False)
def _load_images() -> pd.DataFrame:
    """事前取得済み画像スナップショット（無ければ空 DataFrame）。"""
    return load_heritage_images()


# 地図は st_folium に渡すたびに内部で ``render()`` され _id 等が書き換わるため、
# @st.cache_resource で使い回すと 2 回目以降クリックイベントが取れなくなる。毎回
# build_map で作り直す（重いデータ読込は _load_sites 側でキャッシュ済み）。
# 固定 key を付けているので、地図の pan/zoom や last_object_clicked は再実行を
# またいで保持される。検索での再センタリングは st_folium の center/zoom で行う。


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


st.title("世界遺産マップ")

try:
    sites = _load_sites()
except (FileNotFoundError, ValueError) as exc:
    st.error(f"データの読み込みに失敗しました: {exc}")
    st.stop()

# クリアボタンが押された直後の実行では、検索ボックスの選択もリセットする
# （ウィジェット生成前に session_state を書き換える必要がある）。
if st.session_state.pop(_CLEAR_FLAG_KEY, False):
    st.session_state[_SEARCH_WIDGET_KEY] = None

source_path = PARQUET_PATH if PARQUET_PATH.exists() else SAMPLE_CSV_PATH
fetched_at = (
    datetime.fromtimestamp(source_path.stat().st_mtime, tz=UTC)
    .astimezone()
    .strftime("%Y-%m-%d")
)
_site_labels = {
    int(row.site_id): f"{row.name}（{row.country}）"
    for row in sites.itertuples(index=False)
}

map_col, detail_col = st.columns([2, 1], gap="large")

with map_col:
    st.selectbox(
        "世界遺産を検索",
        options=list(_site_labels),
        index=None,
        format_func=lambda sid: _site_labels[sid],
        placeholder="世界遺産名から検索",
        key=_SEARCH_WIDGET_KEY,
    )

    legend = "　".join(
        f"<span style='color:{CATEGORY_MARKER_COLORS[key]}'>●</span> {label}"
        for key, label in CATEGORY_LABELS_JA.items()
    )
    st.markdown(legend, unsafe_allow_html=True)

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

    # 検索で特定サイトを選んだら、その地点へ地図を寄せる。フォーカスはマーカーを
    # クリックするまで維持する（クリック処理側で解除）。
    picked = st.session_state.get(_SEARCH_WIDGET_KEY)
    if picked is not None and picked != st.session_state.get(_LAST_SEARCH_KEY):
        st.session_state[_LAST_SEARCH_KEY] = picked
        st.session_state[_SELECTED_KEY] = int(picked)
        row = sites.loc[sites["site_id"] == int(picked)].iloc[0]
        st.session_state[_FOCUS_KEY] = [
            float(row["latitude"]),
            float(row["longitude"]),
        ]

    focus_center = st.session_state.get(_FOCUS_KEY)
    focus_zoom = _FOCUS_ZOOM if focus_center is not None else None

    map_state = st_folium(
        build_map(sites),
        use_container_width=True,
        height=650,
        center=focus_center,
        zoom=focus_zoom,
        returned_objects=["last_object_clicked"],
        key=_MAP_WIDGET_KEY,
    )

# マーカークリックの反映。st_folium は再実行後も同じ座標を返し続けるため、
# 直近で処理済みの座標は無視する（「選択をクリア」を効かせるのに必要）。
clicked = (map_state or {}).get("last_object_clicked")
if clicked and clicked != st.session_state.get(_LAST_CLICK_KEY):
    st.session_state[_LAST_CLICK_KEY] = clicked
    # 検索欄の現在値を追認しておき、クリックが検索に上書きされないようにする。
    st.session_state[_LAST_SEARCH_KEY] = st.session_state.get(_SEARCH_WIDGET_KEY)
    # マーカーをクリックしたら検索フォーカスは解除して自由に地図を操作できるようにする。
    st.session_state.pop(_FOCUS_KEY, None)
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
        st.session_state.pop(_SELECTED_KEY, None)
        st.session_state.pop(_FOCUS_KEY, None)
        # 現在のクリック座標・検索値を「処理済み」にして、再実行時の即再選択を防ぐ。
        st.session_state[_LAST_CLICK_KEY] = (map_state or {}).get("last_object_clicked")
        st.session_state[_LAST_SEARCH_KEY] = st.session_state.get(_SEARCH_WIDGET_KEY)
        st.session_state[_CLEAR_FLAG_KEY] = True
        st.rerun()
