"""app.components.detail_panel のユニットテスト。"""

from __future__ import annotations

from streamlit.testing.v1 import AppTest

_SELECTED_SCRIPT = """
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

import pandas as pd

from app.components.detail_panel import render_detail_panel

site = pd.Series(
    {
        "site_id": 661,
        "name": "Himeji-jo",
        "country": "Japan",
        "iso_code": "JP",
        "category": "Cultural",
        "date_inscribed": 1993,
        "latitude": 34.8394,
        "longitude": 134.6939,
        "criteria": "(i)(iv)",
    }
)
render_detail_panel(site)
"""

_EMPTY_SCRIPT = """
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from app.components.detail_panel import render_detail_panel

render_detail_panel(None)
"""

_WITH_IMAGE_SCRIPT = """
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

import pandas as pd

from app.components.detail_panel import render_detail_panel

site = pd.Series(
    {
        "site_id": 661,
        "name": "Himeji-jo",
        "country": "Japan",
        "iso_code": "JP",
        "category": "Cultural",
        "date_inscribed": 1993,
        "latitude": 34.8394,
        "longitude": 134.6939,
        "criteria": "(i)(iv)",
    }
)
image = {
    "image_url": "https://example.org/himeji.jpg",
    "source_page_url": "https://commons.wikimedia.org/wiki/File:Himeji.jpg",
    "license_short_name": "CC BY-SA 4.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/4.0",
    "artist": "Jane Doe",
    "attribution_required": True,
}
render_detail_panel(site, image)
"""


def test_panel_renders_selected_site() -> None:
    at = AppTest.from_string(_SELECTED_SCRIPT).run()
    assert not at.exception
    text = " ".join(m.value for m in at.markdown)
    assert "Himeji-jo" in text
    assert "1993" in text
    assert "文化遺産" in text
    assert "(i)(iv)" in text
    assert "whc.unesco.org/en/list/661" in text


def test_panel_prompts_when_nothing_selected() -> None:
    at = AppTest.from_string(_EMPTY_SCRIPT).run()
    assert not at.exception
    assert any("マーカーをクリック" in info.value for info in at.info)


def test_panel_renders_image_and_credit() -> None:
    at = AppTest.from_string(_WITH_IMAGE_SCRIPT).run()
    assert not at.exception
    captions = " ".join(c.value for c in at.caption)
    assert "Jane Doe" in captions
    assert "CC BY-SA 4.0" in captions
    assert "creativecommons.org/licenses/by-sa/4.0" in captions
    assert "commons.wikimedia.org/wiki/File:Himeji.jpg" in captions


def test_panel_shows_placeholder_when_image_missing() -> None:
    at = AppTest.from_string(_SELECTED_SCRIPT).run()
    assert not at.exception
    captions = " ".join(c.value for c in at.caption)
    assert "取得できませんでした" in captions
