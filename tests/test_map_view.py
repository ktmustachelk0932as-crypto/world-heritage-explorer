"""app.components.map_view のユニットテスト。"""

from __future__ import annotations

import folium
import pandas as pd

from app.components.map_view import CATEGORY_MARKER_COLORS, build_map
from core.data_loader import REQUIRED_COLUMNS

_SAMPLE = pd.DataFrame(
    [
        (661, "Himeji-jo", "Japan", "JP", "Cultural", 1993, 34.8394, 134.6939),
        (
            28,
            "Yellowstone National Park",
            "United States of America",
            "US",
            "Natural",
            1978,
            44.4280,
            -110.5885,
        ),
        (
            274,
            "Historic Sanctuary of Machu Picchu",
            "Peru",
            "PE",
            "Mixed",
            1983,
            -13.1631,
            -72.5450,
        ),
    ],
    columns=list(REQUIRED_COLUMNS),
)


def test_build_map_returns_folium_map() -> None:
    assert isinstance(build_map(_SAMPLE), folium.Map)


def test_map_html_contains_site_names() -> None:
    html = build_map(_SAMPLE).get_root().render()
    assert "Himeji-jo" in html
    assert "Machu Picchu" in html


def test_map_html_uses_category_colors() -> None:
    html = build_map(_SAMPLE).get_root().render()
    for color in CATEGORY_MARKER_COLORS.values():
        assert color in html
