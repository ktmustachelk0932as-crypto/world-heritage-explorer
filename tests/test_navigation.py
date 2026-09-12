"""app/main.py（st.navigation ルーター）のユニットテスト。"""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

_MAIN = str(Path(__file__).resolve().parents[1] / "app" / "main.py")


def test_app_opens_on_map_page_by_default() -> None:
    at = AppTest.from_file(_MAIN, default_timeout=60).run()
    assert not at.exception
    titles = [t.value for t in at.title]
    assert "世界遺産マップ" in titles


def test_app_has_no_landing_page_text() -> None:
    at = AppTest.from_file(_MAIN, default_timeout=60).run()
    body = " ".join(m.value for m in at.markdown)
    assert "サイドバーからページを選択してください。" not in body
