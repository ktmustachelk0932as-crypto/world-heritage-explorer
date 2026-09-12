"""``.env`` ファイルの最小ローダ（外部依存なし）。

``python-dotenv`` を導入せず、``KEY=VALUE`` 形式の行だけを読む。既に設定済みの
環境変数は上書きしない（実際の環境変数・CI・``st.secrets`` 由来を優先）。
"""

from __future__ import annotations

import os
from pathlib import Path

_ENV_PATH: Path = Path(__file__).resolve().parents[1] / ".env"


def load_env_file(path: Path = _ENV_PATH) -> None:
    """``.env`` を読み、未設定のキーのみ ``os.environ`` へ反映する。"""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
