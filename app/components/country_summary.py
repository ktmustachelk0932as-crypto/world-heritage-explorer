"""国別サマリーのグラフ表示（Plotly）。"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from app.components.map_view import CATEGORY_HEX_COLORS, CATEGORY_LABELS_JA
from core.aggregations import CATEGORY_COLUMNS

# 集計列（cultural/natural/mixed）→ 日本語ラベル。地図の凡例と表記を合わせる。
_COLUMN_LABELS_JA: dict[str, str] = {
    CATEGORY_COLUMNS[key]: label for key, label in CATEGORY_LABELS_JA.items()
}

# 分類ごとの色（日本語ラベル→hex）。地図マーカーの色に対応させる。
_CATEGORY_COLORS_JA: dict[str, str] = {
    CATEGORY_LABELS_JA[key]: color for key, color in CATEGORY_HEX_COLORS.items()
}


def render_country_bar_chart(summary: pd.DataFrame, *, top_n: int = 20) -> None:
    """国別の登録件数を、分類内訳で色分けした積み上げ横棒グラフで表示する。

    Args:
        summary: ``core.aggregations.summarize_by_country`` が返す DataFrame。
        top_n: 表示する上位の国数。
    """
    st.subheader(f"登録件数の多い国（上位 {top_n}）")
    if summary.empty:
        st.info("表示できるデータがありません。")
        return

    top = summary.head(top_n)
    long_df = top.melt(
        id_vars=["country"],
        value_vars=list(CATEGORY_COLUMNS.values()),
        var_name="category",
        value_name="count",
    )
    long_df["category"] = long_df["category"].map(_COLUMN_LABELS_JA)

    fig = px.bar(
        long_df,
        x="count",
        y="country",
        color="category",
        orientation="h",
        color_discrete_map=_CATEGORY_COLORS_JA,
        category_orders={
            # px.bar(orientation="h") はこのリストを y 軸で反転させるため、
            # 登録件数の降順（＝summary の並び）をそのまま渡すと最多件数国が最上段になる。
            "country": top["country"].tolist(),
            "category": list(_CATEGORY_COLORS_JA),
        },
        labels={"count": "登録件数", "country": "国 / 地域", "category": "分類"},
    )
    fig.update_layout(
        barmode="stack",
        height=max(360, 26 * len(top)),
        legend_title_text="",
        margin={"l": 8, "r": 8, "t": 8, "b": 8},
    )
    st.plotly_chart(fig, width="stretch")


def render_country_detail(
    sites: pd.DataFrame, summary: pd.DataFrame, country: str
) -> None:
    """選択された国の登録件数・分類内訳・遺産一覧を表示する。

    Args:
        sites: ``core.data_loader.load_heritage_sites`` が返す DataFrame。
        summary: ``core.aggregations.summarize_by_country`` が返す DataFrame。
        country: 対象の国名（``summary["country"]`` の値）。
    """
    st.subheader(country)

    rows = summary[summary["country"] == country]
    if rows.empty:
        st.info("該当する国のデータがありません。")
        return
    row = rows.iloc[0]

    cols = st.columns(4)
    cols[0].metric("登録件数", int(row["total"]))
    cols[1].metric(CATEGORY_LABELS_JA["Cultural"], int(row["cultural"]))
    cols[2].metric(CATEGORY_LABELS_JA["Natural"], int(row["natural"]))
    cols[3].metric(CATEGORY_LABELS_JA["Mixed"], int(row["mixed"]))

    breakdown = pd.DataFrame(
        {
            "category": [
                CATEGORY_LABELS_JA["Cultural"],
                CATEGORY_LABELS_JA["Natural"],
                CATEGORY_LABELS_JA["Mixed"],
            ],
            "count": [
                int(row["cultural"]),
                int(row["natural"]),
                int(row["mixed"]),
            ],
        }
    )
    breakdown = breakdown[breakdown["count"] > 0]
    if not breakdown.empty:
        fig = px.pie(
            breakdown,
            names="category",
            values="count",
            color="category",
            color_discrete_map=_CATEGORY_COLORS_JA,
        )
        fig.update_layout(
            height=280,
            legend_title_text="",
            margin={"l": 8, "r": 8, "t": 8, "b": 8},
        )
        st.plotly_chart(fig, width="stretch")

    country_sites = (
        sites[sites["country"] == country]
        .loc[:, ["date_inscribed", "name", "category"]]
        .sort_values(["date_inscribed", "name"])
        .reset_index(drop=True)
    )
    country_sites["category"] = country_sites["category"].map(
        lambda key: CATEGORY_LABELS_JA.get(str(key), str(key))
    )
    # 年は桁区切りを付けずに表示する。
    country_sites["date_inscribed"] = country_sites["date_inscribed"].astype(str)
    country_sites = country_sites.rename(
        columns={"date_inscribed": "登録年", "name": "名称", "category": "分類"}
    )
    st.dataframe(country_sites, width="stretch", hide_index=True)
