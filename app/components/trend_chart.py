"""年次推移グラフ（分類別の積み上げエリアチャート、Plotly）。"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from app.components.map_view import (
    CATEGORY_COLORS_BY_LABEL_JA,
    CATEGORY_COLUMN_LABELS_JA,
)
from core.aggregations import CATEGORY_COLUMNS


def render_trend_chart(yearly: pd.DataFrame) -> None:
    """累積登録数の年次推移を、分類（文化/自然/複合）別の積み上げエリアで表示する。

    Args:
        yearly: ``core.aggregations.yearly_counts(..., cumulative=True)`` が返す
            DataFrame（累積化は ``yearly_counts`` 側で行う）。
    """
    if yearly.empty:
        st.info("表示できるデータがありません。")
        return

    long_df = yearly.melt(
        id_vars=["year"],
        value_vars=list(CATEGORY_COLUMNS.values()),
        var_name="category",
        value_name="count",
    )
    long_df["category"] = long_df["category"].map(CATEGORY_COLUMN_LABELS_JA)
    fig = px.area(
        long_df,
        x="year",
        y="count",
        color="category",
        color_discrete_map=CATEGORY_COLORS_BY_LABEL_JA,
        category_orders={"category": list(CATEGORY_COLORS_BY_LABEL_JA)},
        labels={"year": "年", "count": "累積登録数", "category": "分類"},
    )
    fig.update_layout(
        height=420,
        legend_title_text="",
        margin={"l": 8, "r": 8, "t": 8, "b": 8},
        hovermode="x unified",
    )
    st.plotly_chart(fig, width="stretch")
