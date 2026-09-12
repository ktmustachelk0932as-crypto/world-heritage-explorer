"""国別集計・年次集計ロジック（Streamlit 非依存）。"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

# 分類の内部キー（元データの category 値）と、集計結果での列名。
CATEGORY_KEYS: tuple[str, ...] = ("Cultural", "Natural", "Mixed")
CATEGORY_COLUMNS: dict[str, str] = {
    "Cultural": "cultural",
    "Natural": "natural",
    "Mixed": "mixed",
}

COUNTRY_SUMMARY_COLUMNS: tuple[str, ...] = (
    "country",
    "iso_code",
    "total",
    "cultural",
    "natural",
    "mixed",
)

YEARLY_COUNTS_COLUMNS: tuple[str, ...] = (
    "year",
    "cultural",
    "natural",
    "mixed",
    "total",
)


def summarize_by_country(df: pd.DataFrame) -> pd.DataFrame:
    """国別に登録件数と分類内訳を集計する。

    Args:
        df: ``core.data_loader.load_heritage_sites`` が返す形式の DataFrame。

    Returns:
        1 行 = 1 国の DataFrame（列 ``COUNTRY_SUMMARY_COLUMNS``）。
        ``total`` 降順、同数なら ``country`` 昇順でソートする。
        入力が空の場合は列だけ揃えた空の DataFrame を返す。
    """
    if df.empty:
        return _empty_frame(
            COUNTRY_SUMMARY_COLUMNS, object_columns=("country", "iso_code")
        )

    counts = _category_pivot(df, ["country", "iso_code"])
    counts["total"] = counts.sum(axis=1)

    result = counts.reset_index()
    result = result.sort_values(
        ["total", "country"], ascending=[False, True]
    ).reset_index(drop=True)
    return result[list(COUNTRY_SUMMARY_COLUMNS)]


def count_by_category(df: pd.DataFrame) -> dict[str, int]:
    """分類ごとの登録件数を返す（全分類のキーを必ず含む）。

    Args:
        df: ``core.data_loader.load_heritage_sites`` が返す形式の DataFrame。

    Returns:
        ``{"Cultural": n, "Natural": n, "Mixed": n}``。
    """
    counts = df["category"].value_counts()
    return {key: int(counts.get(key, 0)) for key in CATEGORY_KEYS}


def yearly_counts(
    df: pd.DataFrame,
    *,
    country: str | None = None,
    cumulative: bool = False,
) -> pd.DataFrame:
    """年ごとの登録件数を分類内訳付きで集計する。

    Args:
        df: ``core.data_loader.load_heritage_sites`` が返す形式の DataFrame。
        country: 指定するとその国のみを集計する。``None`` なら全世界。
        cumulative: ``True`` なら各年までの累積件数を返す。

    Returns:
        1 行 = 1 年の DataFrame（列 ``YEARLY_COUNTS_COLUMNS``、``year`` 昇順）。
        登録のない中間年も 0 で埋める。該当データが無い場合は列だけ揃えた
        空の DataFrame を返す。
    """
    if country is not None:
        df = df[df["country"] == country]
    if df.empty:
        return _empty_frame(YEARLY_COUNTS_COLUMNS)

    counts = _category_pivot(df, ["date_inscribed"])

    full_years = range(int(counts.index.min()), int(counts.index.max()) + 1)
    counts = counts.reindex(full_years, fill_value=0)
    counts.index.name = "year"
    counts["total"] = counts.sum(axis=1)

    if cumulative:
        counts = counts.cumsum()

    return counts.reset_index()[list(YEARLY_COUNTS_COLUMNS)]


def _category_pivot(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    """``by`` × 分類で件数を集計し、分類 3 列（``CATEGORY_COLUMNS`` の値）を必ず持つ表にする。"""
    counts = df.groupby([*by, "category"]).size().unstack(fill_value=0)
    return counts.reindex(columns=list(CATEGORY_KEYS), fill_value=0).rename(
        columns=CATEGORY_COLUMNS
    )


def _empty_frame(
    columns: Sequence[str], *, object_columns: Sequence[str] = ()
) -> pd.DataFrame:
    """列だけ揃えた空の DataFrame（``object_columns`` 以外は int64）。"""
    return pd.DataFrame(
        {
            col: pd.Series(dtype="object" if col in object_columns else "int64")
            for col in columns
        }
    )
