"""年次推移グラフ（折れ線・エリアチャート、Plotly）。"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from app.components.map_view import CATEGORY_HEX_COLORS, CATEGORY_LABELS_JA
from core.aggregations import CATEGORY_COLUMNS

# 集計列（cultural/natural/mixed）→ 日本語ラベル。
_COLUMN_LABELS_JA: dict[str, str] = {
    CATEGORY_COLUMNS[key]: label for key, label in CATEGORY_LABELS_JA.items()
}

# 分類ごとの色（日本語ラベル→hex）。地図・国別サマリーと揃える。
_CATEGORY_COLORS_JA: dict[str, str] = {
    CATEGORY_LABELS_JA[key]: color for key, color in CATEGORY_HEX_COLORS.items()
}

_TOTAL_COLOR: str = "#4c78a8"


def render_trend_chart(
    yearly: pd.DataFrame,
    *,
    cumulative: bool = False,
    show_breakdown: bool = False,
) -> None:
    """年次の登録件数を折れ線／エリアチャートで表示する。

    Args:
        yearly: ``core.aggregations.yearly_counts`` が返す DataFrame。
        cumulative: ``True`` なら累積件数として軸ラベルを表示する
            （実際の累積化は ``yearly_counts`` 側で行う）。
        show_breakdown: ``True`` なら分類（文化/自然/複合）別の積み上げエリア、
            ``False`` なら合計の折れ線＋エリアで表示する。
    """
    y_label = "累積登録数" if cumulative else "登録数"

    if yearly.empty:
        st.info("表示できるデータがありません。")
        return

    if show_breakdown:
        long_df = yearly.melt(
            id_vars=["year"],
            value_vars=list(CATEGORY_COLUMNS.values()),
            var_name="category",
            value_name="count",
        )
        long_df["category"] = long_df["category"].map(_COLUMN_LABELS_JA)
        fig = px.area(
            long_df,
            x="year",
            y="count",
            color="category",
            color_discrete_map=_CATEGORY_COLORS_JA,
            category_orders={"category": list(_CATEGORY_COLORS_JA)},
            labels={"year": "年", "count": y_label, "category": "分類"},
        )
    else:
        fig = px.area(
            yearly,
            x="year",
            y="total",
            labels={"year": "年", "total": y_label},
        )
        fig.update_traces(
            line_color=_TOTAL_COLOR,
            fillcolor="rgba(76, 120, 168, 0.25)",
        )

    fig.update_layout(
        height=420,
        legend_title_text="",
        margin={"l": 8, "r": 8, "t": 8, "b": 8},
        hovermode="x unified",
    )
    st.plotly_chart(fig, width="stretch")
