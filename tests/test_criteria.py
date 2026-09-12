"""core.criteria のユニットテスト。"""

from __future__ import annotations

from core.criteria import CRITERIA_DESCRIPTIONS_JA, describe_criteria


def test_all_ten_criteria_have_descriptions() -> None:
    expected = {
        f"({r})" for r in ("i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x")
    }
    assert set(CRITERIA_DESCRIPTIONS_JA) == expected
    assert all(v.endswith("。") for v in CRITERIA_DESCRIPTIONS_JA.values())


def test_describe_splits_and_preserves_order() -> None:
    result = describe_criteria("(i)(iv)")
    assert [token for token, _ in result] == ["(i)", "(iv)"]
    assert result[0][1] == CRITERIA_DESCRIPTIONS_JA["(i)"]


def test_describe_ignores_unknown_tokens_and_dedupes() -> None:
    assert describe_criteria("(i)(zz)(i)") == [("(i)", CRITERIA_DESCRIPTIONS_JA["(i)"])]


def test_describe_handles_empty() -> None:
    assert describe_criteria("") == []
    assert describe_criteria(None) == []  # type: ignore[arg-type]
