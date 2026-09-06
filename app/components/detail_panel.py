"""詳細情報パネル（名称・登録年・国・分類・登録基準のテキスト＋代表画像）。"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.components.map_view import CATEGORY_LABELS_JA

_UNESCO_SITE_URL = "https://whc.unesco.org/en/list/{site_id}"


def render_detail_panel(site: pd.Series | None) -> None:
    """選択された世界遺産サイトの詳細をテキストで表示する。

    Args:
        site: ``core.data_loader.load_heritage_sites`` の 1 行。未選択時は ``None``。
    """
    st.subheader("詳細情報")

    if site is None:
        st.info("地図上のマーカーをクリックすると詳細が表示されます。")
        return

    category = CATEGORY_LABELS_JA.get(str(site["category"]), str(site["category"]))
    criteria = str(site.get("criteria", "") or "")

    st.markdown(f"### {site['name']}")
    st.markdown(f"**国 / 地域**: {site['country']}")
    st.markdown(f"**登録年**: {int(site['date_inscribed'])}")
    st.markdown(f"**分類**: {category}")
    if criteria:
        st.markdown(f"**登録基準**: {criteria}")

    site_id = int(site["site_id"])
    st.markdown(f"[UNESCO 公式ページ]({_UNESCO_SITE_URL.format(site_id=site_id)})")
    st.caption(f"UNESCO ID: {site_id}")
