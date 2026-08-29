"""folium地図の描画とクリックイベント処理。"""

from __future__ import annotations

import html

import folium
import pandas as pd
from folium.plugins import MarkerCluster

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

_DEFAULT_CENTER: tuple[float, float] = (20.0, 0.0)
_DEFAULT_ZOOM: int = 2


def build_map(df: pd.DataFrame) -> folium.Map:
    """世界遺産サイトをマーカー表示した folium 地図を組み立てる。

    Args:
        df: ``core.data_loader.load_heritage_sites`` が返す形式の DataFrame。

    Returns:
        マーカー（分類ごとに色分け・クラスタリング）を載せた ``folium.Map``。
    """
    fmap = folium.Map(
        location=list(_DEFAULT_CENTER),
        zoom_start=_DEFAULT_ZOOM,
        tiles="cartodbpositron",
        world_copy_jump=True,
        control_scale=True,
    )
    cluster = MarkerCluster(name="世界遺産").add_to(fmap)

    for row in df.itertuples(index=False):
        color = CATEGORY_MARKER_COLORS.get(row.category, UNKNOWN_MARKER_COLOR)
        folium.Marker(
            location=[row.latitude, row.longitude],
            tooltip=html.escape(str(row.name)),
            popup=folium.Popup(_popup_html(row), max_width=300),
            icon=folium.Icon(color=color, icon="info-sign"),
        ).add_to(cluster)

    return fmap


def _popup_html(row: tuple) -> str:  # namedtuple row from itertuples
    """マーカーのポップアップに表示する HTML を生成する（値はエスケープ済み）。"""
    name = html.escape(str(row.name))
    country = html.escape(str(row.country))
    category = html.escape(CATEGORY_LABELS_JA.get(row.category, str(row.category)))
    year = html.escape(str(row.date_inscribed))
    return f"<b>{name}</b><br>国: {country}<br>登録年: {year}<br>分類: {category}"
