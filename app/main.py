"""streamlit run のエントリーポイント。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

st.set_page_config(
    page_title="世界遺産可視化アプリ",
    page_icon="🌍",
    layout="wide",
)

st.title("世界遺産可視化アプリ")
st.markdown("サイドバーからページを選択してください。")
