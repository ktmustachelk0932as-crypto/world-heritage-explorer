"""streamlit run のエントリーポイント（ページのルーティングのみ）。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

st.set_page_config(
    page_title="世界遺産可視化アプリ",
    page_icon="🌍",
    layout="wide",
)

# 起動時は地図ページを開く（案内用のトップページは設けない）。
pages = [
    st.Page("views/map.py", title="地図", icon="🗺️", default=True),
    st.Page("views/country.py", title="国別サマリー", icon="🌐"),
    st.Page("views/trend.py", title="登録推移", icon="📈"),
]
st.navigation(pages).run()
