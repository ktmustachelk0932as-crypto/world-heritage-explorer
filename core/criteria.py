"""世界遺産の登録基準 (i)〜(x) の日本語説明。

UNESCO「世界遺産条約履行のための作業指針」の登録基準に基づく要約。
``criteria`` 列（例 ``"(i)(iv)"``）を人間が読める説明に変換する。
"""

from __future__ import annotations

import re

# (i)〜(vi) が文化遺産の基準、(vii)〜(x) が自然遺産の基準。
CRITERIA_DESCRIPTIONS_JA: dict[str, str] = {
    "(i)": "人類の創造的才能を表す傑作である。",
    "(ii)": "建築・技術・記念碑・都市計画・景観設計の発展において、"
    "ある期間または世界の文化圏内での重要な価値観の交流を示す。",
    "(iii)": "現存する、または消滅した文化的伝統や文明の、"
    "唯一のまたは少なくとも稀有な証拠である。",
    "(iv)": "人類の歴史上の重要な段階を物語る建築様式・技術の集積体・"
    "景観の顕著な見本である。",
    "(v)": "特に不可逆的な変化により存続が危ぶまれている、"
    "ある文化（複数の文化）を代表する伝統的集落・土地利用・海洋利用の顕著な見本である。",
    "(vi)": "顕著な普遍的意義を有する出来事、生きた伝統、思想、信仰、"
    "芸術的・文学的作品と直接または実質的に関連する。",
    "(vii)": "類いまれな自然美・美的価値をもつ傑出した自然現象または地域である。",
    "(viii)": "生命の記録、地形形成における重要な地質学的過程、"
    "重要な地形学的・自然地理学的特徴など、地球の歴史の主要な段階を代表する顕著な見本である。",
    "(ix)": "陸上・淡水・沿岸・海洋の生態系や動植物群集の進化・発展において、"
    "重要な進行中の生態学的・生物学的過程を代表する顕著な見本である。",
    "(x)": "学術上・保全上顕著な普遍的価値をもつ絶滅危惧種の生育・生息地など、"
    "生物多様性の生息域内保全にとって最も重要な自然生息地を含む。",
}

_TOKEN_RE = re.compile(r"\((?:i{1,3}|iv|v|vi{0,3}|ix|x)\)")


def describe_criteria(criteria: str) -> list[tuple[str, str]]:
    """``"(i)(iv)"`` を ``[("(i)", 説明), ("(iv)", 説明)]`` に分解する。

    未知のトークンや説明の無いトークンは結果に含めない。出現順・重複除去。
    """
    seen: set[str] = set()
    result: list[tuple[str, str]] = []
    for token in _TOKEN_RE.findall(criteria or ""):
        if token in seen:
            continue
        seen.add(token)
        description = CRITERIA_DESCRIPTIONS_JA.get(token)
        if description:
            result.append((token, description))
    return result
