"""core.data_loader のユニットテスト。"""

from __future__ import annotations

import pandas as pd

from core.data_loader import ALLOWED_CATEGORIES, REQUIRED_COLUMNS, load_heritage_sites


def test_returns_non_empty_dataframe() -> None:
    df = load_heritage_sites()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_has_required_columns() -> None:
    df = load_heritage_sites()
    assert list(df.columns) == list(REQUIRED_COLUMNS)


def test_coordinates_are_present_and_in_range() -> None:
    df = load_heritage_sites()
    assert df["latitude"].notna().all()
    assert df["longitude"].notna().all()
    assert df["latitude"].between(-90, 90).all()
    assert df["longitude"].between(-180, 180).all()


def test_categories_are_allowed() -> None:
    df = load_heritage_sites()
    assert set(df["category"]).issubset(ALLOWED_CATEGORIES)


def test_dtypes() -> None:
    df = load_heritage_sites()
    assert df["site_id"].dtype == "int64"
    assert df["date_inscribed"].dtype == "int64"
    assert df["latitude"].dtype == "float64"
    assert df["longitude"].dtype == "float64"
