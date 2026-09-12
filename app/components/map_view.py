"""folium地図の描画とクリックイベント処理。"""

from __future__ import annotations

import html

import folium
import pandas as pd
from folium.plugins import MarkerCluster

from core.aggregations import CATEGORY_COLUMNS

CATEGORY_MARKER_COLORS: dict[str, str] = {
    "Cultural": "blue",
    "Natural": "green",
    "Mixed": "purple",
}
UNKNOWN_MARKER_COLOR: str = "gray"

CATEGORY_LABELS_JA: dict[str, str] = {
    "Cultural": "文化遺産",
    "Natural": "自然遺産",
    "Mixed": "複合遺産",
}

# Plotly など hex 前提のグラフで使う分類色（folium マーカーの色名に対応させる）。
CATEGORY_HEX_COLORS: dict[str, str] = {
    "Cultural": "#1f77b4",
    "Natural": "#2ca02c",
    "Mixed": "#9467bd",
}

# 集計列（cultural/natural/mixed）→ 日本語ラベル。グラフの表記を地図の凡例と合わせる。
CATEGORY_COLUMN_LABELS_JA: dict[str, str] = {
    CATEGORY_COLUMNS[key]: label for key, label in CATEGORY_LABELS_JA.items()
}

# 日本語ラベル → hex 色。Plotly の color_discrete_map 用。
CATEGORY_COLORS_BY_LABEL_JA: dict[str, str] = {
    CATEGORY_LABELS_JA[key]: color for key, color in CATEGORY_HEX_COLORS.items()
}

_DEFAULT_CENTER: tuple[float, float] = (20.0, 0.0)
_DEFAULT_ZOOM: int = 2
# これ以上引くと世界地図が複数枚並ぶ（タイルの水平リピート）ため下限を設ける。
_MIN_ZOOM: int = 2
# このズーム以上ではクラスタリングを止めて全マーカーを個別表示する。検索で寄せた
# 直後に選択した遺産がクラスタに埋もれないよう、地図ページのフォーカス倍率
# （app/views/map.py の _FOCUS_ZOOM）はこの値以上にすること。
CLUSTER_DISABLE_ZOOM: int = 10

# クリック座標とマーカー座標を突き合わせる際の許容誤差（度）。
_COORD_TOLERANCE: float = 1e-6


def build_map(df: pd.DataFrame) -> folium.Map:
    """世界遺産サイトをマーカー表示した folium 地図を組み立てる。

    Args:
        df: ``core.data_loader.load_heritage_sites`` が返す形式の DataFrame。

    Returns:
        マーカー（分類ごとに色分け・クラスタリング）を載せた ``folium.Map``。
        表示位置の変更（検索でのフォーカス等）は ``st_folium`` の center/zoom で行う。
    """
    fmap = folium.Map(
        location=list(_DEFAULT_CENTER),
        zoom_start=_DEFAULT_ZOOM,
        min_zoom=_MIN_ZOOM,
        max_bounds=True,
        tiles=None,
        control_scale=True,
    )
    # OpenStreetMap（キー不要・カラー・帰属表示自動）。no_wrap で東西の無限リピート、
    # min_zoom で世界地図が複数枚並ぶズームレベルへの縮小を止める。
    folium.TileLayer(
        "OpenStreetMap", no_wrap=True, min_zoom=_MIN_ZOOM, control=False
    ).add_to(fmap)
    cluster = MarkerCluster(
        name="世界遺産",
        options={"disableClusteringAtZoom": CLUSTER_DISABLE_ZOOM},
    ).add_to(fmap)

    for row in df.itertuples(index=False):
        color = CATEGORY_MARKER_COLORS.get(row.category, UNKNOWN_MARKER_COLOR)
        folium.Marker(
            location=[row.latitude, row.longitude],
            tooltip=html.escape(str(row.name)),
            popup=folium.Popup(_popup_html(row), max_width=300),
            icon=folium.Icon(color=color, icon="info-sign"),
        ).add_to(cluster)

    return fmap


def find_site_by_coordinates(
    df: pd.DataFrame,
    lat: float,
    lng: float,
    *,
    tolerance: float = _COORD_TOLERANCE,
) -> pd.Series | None:
    """``st_folium`` のクリック座標から該当する世界遺産サイトの行を返す。

    マーカーは ``build_map`` が ``df`` の緯度経度をそのまま使って配置するため、
    クリック時に返る座標も許容誤差の範囲で一致する。

    Args:
        df: ``core.data_loader.load_heritage_sites`` が返す形式の DataFrame。
        lat: クリックされたマーカーの緯度（``last_object_clicked`` の ``lat``）。
        lng: クリックされたマーカーの経度（``last_object_clicked`` の ``lng``）。
        tolerance: 座標一致とみなす絶対誤差（度）。

    Returns:
        一致した最初の行（``pd.Series``）。一致しなければ ``None``。
    """
    match = df[
        (df["latitude"] - lat).abs().le(tolerance)
        & (df["longitude"] - lng).abs().le(tolerance)
    ]
    if match.empty:
        return None
    return match.iloc[0]


def _popup_html(row: tuple) -> str:  # namedtuple row from itertuples
    """マーカーのポップアップに表示する HTML を生成する（値はエスケープ済み）。"""
    name = html.escape(str(row.name))
    country = html.escape(str(row.country))
    category = html.escape(CATEGORY_LABELS_JA.get(row.category, str(row.category)))
    year = html.escape(str(row.date_inscribed))
    return f"<b>{name}</b><br>国: {country}<br>登録年: {year}<br>分類: {category}"
