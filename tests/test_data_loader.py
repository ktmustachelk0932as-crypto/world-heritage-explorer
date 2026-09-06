"""core.data_loader のユニットテスト。"""

from __future__ import annotations

import pandas as pd
import pytest

from core import data_loader
from core.data_loader import (
    ALLOWED_CATEGORIES,
    IMAGE_COLUMNS,
    OPTIONAL_COLUMNS,
    REQUIRED_COLUMNS,
    load_heritage_images,
    load_heritage_sites,
)


def test_returns_non_empty_dataframe() -> None:
    df = load_heritage_sites()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_has_required_columns() -> None:
    df = load_heritage_sites()
    assert set(REQUIRED_COLUMNS).issubset(df.columns)


def test_optional_columns_always_present() -> None:
    df = load_heritage_sites()
    for col in OPTIONAL_COLUMNS:
        assert col in df.columns
        assert df[col].notna().all()


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


def test_load_heritage_images_returns_empty_frame_when_snapshot_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    monkeypatch.setattr(
        data_loader, "IMAGES_PARQUET_PATH", tmp_path / "does_not_exist.parquet"
    )
    df = load_heritage_images()
    assert list(df.columns) == list(IMAGE_COLUMNS)
    assert df.empty
    assert df["site_id"].dtype == "int64"
    assert df["attribution_required"].dtype == "bool"


def test_load_heritage_images_reads_and_coerces_snapshot(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    path = tmp_path / "heritage_images.parquet"
    pd.DataFrame(
        {
            "site_id": ["661", "1"],
            "image_url": ["https://example.org/himeji.jpg", ""],
            "source_page_url": ["https://commons.example/File:Himeji", ""],
            "license_short_name": ["CC BY-SA 4.0", ""],
            "license_url": ["https://creativecommons.org/licenses/by-sa/4.0", ""],
            "artist": ["Someone", ""],
            "attribution_required": [True, False],
            "retrieved_at": ["2026-09-06T00:00:00+00:00", "2026-09-06T00:00:00+00:00"],
        }
    ).to_parquet(path, index=False)
    monkeypatch.setattr(data_loader, "IMAGES_PARQUET_PATH", path)

    df = load_heritage_images()

    # image_url が空の行は落ちる。
    assert df["site_id"].tolist() == [661]
    assert df["site_id"].dtype == "int64"
    assert df["attribution_required"].dtype == "bool"
    assert df.iloc[0]["license_short_name"] == "CC BY-SA 4.0"
