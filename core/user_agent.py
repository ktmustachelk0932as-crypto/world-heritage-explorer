"""Wikimedia 系 API へのリクエストで共有する User-Agent の組み立て。

Wikimedia の利用規約では、連絡先を含む User-Agent の送出が推奨されている。
連絡先は環境変数 ``WIKIMEDIA_CONTACT_EMAIL`` から読み取る（未設定でも処理は継続し、
警告ログのみ出す）。
"""

from __future__ import annotations

import logging
import os

LOGGER = logging.getLogger(__name__)

_APP_TOKEN = "world-heritage-explorer/0.1"

_missing_contact_warned = False


def build_user_agent() -> str:
    """連絡先を含む User-Agent 文字列を返す。

    環境変数 ``WIKIMEDIA_CONTACT_EMAIL`` が未設定の場合は（プロセス内で一度だけ）
    警告ログを出し、連絡先なしの文字列を返す（処理は中断しない）。
    """
    global _missing_contact_warned

    contact = os.environ.get("WIKIMEDIA_CONTACT_EMAIL", "").strip()
    if not contact:
        if not _missing_contact_warned:
            LOGGER.warning(
                "WIKIMEDIA_CONTACT_EMAIL が未設定です。"
                "Wikimedia の利用規約では連絡先を含む User-Agent が推奨されています。"
            )
            _missing_contact_warned = True
        return f"{_APP_TOKEN} (no contact email set)"
    return f"{_APP_TOKEN} (contact: {contact})"
