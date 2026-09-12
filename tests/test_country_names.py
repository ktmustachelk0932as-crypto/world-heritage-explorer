"""core.country_names のユニットテスト。"""

from __future__ import annotations

from core.country_names import COUNTRY_NAMES_JA, localize_country


def test_known_codes_resolve_to_japanese() -> None:
    assert localize_country("JP", "Japan") == "日本"
    assert localize_country("FR", "France") == "フランス"
    assert localize_country("US", "United States of America") == "アメリカ合衆国"
    assert localize_country("GB", "United Kingdom") == "イギリス"


def test_unknown_code_falls_back_to_given_name() -> None:
    assert localize_country("XX", "Neverland") == "Neverland"
    assert localize_country("", "Neverland") == "Neverland"


def test_code_is_normalised() -> None:
    assert localize_country(" jp ", "Japan") == "日本"


def test_all_values_are_non_empty_japanese() -> None:
    for code, name in COUNTRY_NAMES_JA.items():
        assert len(code) == 2 and code.isupper()
        assert name and name.strip() == name
