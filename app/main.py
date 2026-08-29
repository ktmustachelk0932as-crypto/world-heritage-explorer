"""streamlit run のエントリーポイント。"""

import streamlit as st

st.set_page_config(
    page_title="世界遺産可視化アプリ",
    page_icon="🌍",
    layout="wide",
)

st.title("世界遺産可視化アプリ")
st.markdown("サイドバーからページを選択してください。")
