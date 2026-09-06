"""UNESCO World Heritage List・国土数値情報の読み込みと整形。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROCESSED_DIR: Path = Path(__file__).resolve().parents[1] / "data" / "processed"
PARQUET_PATH: Path = PROCESSED_DIR / "heritage_sites.parquet"
SAMPLE_CSV_PATH: Path = PROCESSED_DIR / "heritage_sites_sample.csv"

REQUIRED_COLUMNS: tuple[str, ...] = (
    "site_id",
    "name",
    "country",
    "iso_code",
    "category",
    "date_inscribed",
    "latitude",
    "longitude",
)

# 元データにあれば値を引き継ぎ、無ければ空文字で必ず用意する任意列。
OPTIONAL_COLUMNS: tuple[str, ...] = ("criteria",)

ALLOWED_CATEGORIES: frozenset[str] = frozenset({"Cultural", "Natural", "Mixed"})


def load_heritage_sites() -> pd.DataFrame:
    """世界遺産サイトの一覧を整形済み DataFrame として返す。

    整形済み parquet があればそれを、無ければ同梱のサンプル CSV を読み込む。
    緯度経度が欠損・範囲外の行、未知の分類の行は除外する。

    Returns:
        列 ``REQUIRED_COLUMNS`` ＋ ``OPTIONAL_COLUMNS`` を持つ DataFrame。
        ``date_inscribed`` は int、``latitude`` / ``longitude`` は float。

    Raises:
        FileNotFoundError: parquet・サンプル CSV のどちらも存在しない場合。
        ValueError: 必須列が欠けている場合。
    """
    source = _resolve_source()
    if source.suffix == ".parquet":
        df = pd.read_parquet(source)
    else:
        df = pd.read_csv(source)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{source.name} に必須列がありません: {', '.join(missing)}")

    present_optional = [c for c in OPTIONAL_COLUMNS if c in df.columns]
    df = df.loc[:, [*REQUIRED_COLUMNS, *present_optional]].copy()

    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["date_inscribed"] = pd.to_numeric(df["date_inscribed"], errors="coerce")

    valid = (
        df["latitude"].notna()
        & df["longitude"].notna()
        & df["date_inscribed"].notna()
        & df["latitude"].between(-90, 90)
        & df["longitude"].between(-180, 180)
        & df["category"].isin(ALLOWED_CATEGORIES)
    )
    df = df.loc[valid].copy()

    df["site_id"] = df["site_id"].astype(int)
    df["date_inscribed"] = df["date_inscribed"].astype(int)
    df["latitude"] = df["latitude"].astype(float)
    df["longitude"] = df["longitude"].astype(float)
    for col in ("name", "country", "iso_code", "category"):
        df[col] = df[col].astype(str)

    for col in OPTIONAL_COLUMNS:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)
        else:
            df[col] = ""

    return df.sort_values("site_id").reset_index(drop=True)


def _resolve_source() -> Path:
    """読み込むデータファイルを決定する（parquet 優先、無ければサンプル CSV）。"""
    if PARQUET_PATH.exists():
        return PARQUET_PATH
    if SAMPLE_CSV_PATH.exists():
        return SAMPLE_CSV_PATH
    raise FileNotFoundError(
        "世界遺産データが見つかりません。"
        f"{PARQUET_PATH} または {SAMPLE_CSV_PATH} を用意してください。"
    )
