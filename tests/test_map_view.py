"""app.components.map_view のユニットテスト。"""

from __future__ import annotations

import folium
import pandas as pd

from app.components.map_view import (
    CATEGORY_MARKER_COLORS,
    build_map,
    find_site_by_coordinates,
)
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


def test_map_uses_openstreetmap_without_wrapping() -> None:
    html = build_map(_SAMPLE).get_root().render()
    assert "openstreetmap.org" in html.lower()
    assert "cartodb" not in html.lower()
    assert '"noWrap": true' in html
    assert '"minZoom": 2' in html
    assert "worldCopyJump" not in html


def test_find_site_by_coordinates_exact_match() -> None:
    site = find_site_by_coordinates(_SAMPLE, 34.8394, 134.6939)
    assert site is not None
    assert site["name"] == "Himeji-jo"


def test_find_site_by_coordinates_within_tolerance() -> None:
    site = find_site_by_coordinates(_SAMPLE, 34.8394 + 1e-7, 134.6939 - 1e-7)
    assert site is not None
    assert int(site["site_id"]) == 661


def test_find_site_by_coordinates_no_match() -> None:
    assert find_site_by_coordinates(_SAMPLE, 0.0, 0.0) is None
