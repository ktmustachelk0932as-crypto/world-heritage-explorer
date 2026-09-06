"""core.site_names_ja と、遺産名の和名化のユニットテスト。"""

from __future__ import annotations

import re

from core.data_loader import load_heritage_sites
from core.site_names_ja import SITE_NAMES_JA

_JP_RE = re.compile(r"[぀-ゟ゠-ヿ㐀-鿿豈-﫿]")


def test_override_values_contain_japanese() -> None:
    assert SITE_NAMES_JA
    for site_id, name in SITE_NAMES_JA.items():
        assert isinstance(site_id, int)
        assert _JP_RE.search(name), f"{site_id}: {name!r}"
        assert name.strip() == name and " " not in name


def test_loaded_names_are_japanese() -> None:
    """override 適用後、英語のまま残る遺産名が無いこと。"""
    df = load_heritage_sites()
    english_only = [n for n in df["name"] if not _JP_RE.search(str(n))]
    assert english_only == []


def test_loaded_countries_are_japanese() -> None:
    df = load_heritage_sites()
    english_only = [c for c in df["country"].unique() if not _JP_RE.search(str(c))]
    assert english_only == []
