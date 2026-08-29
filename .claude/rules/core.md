---
paths:
  - "core/**"
---

# core/ のルール

- `core/` はStreamlitに依存させない。`st.*` を含むコードを書かない（UIは `app/` 配下）
- Wikipedia APIの呼び出しは `core/image_fetcher.py` 経由に限定し、逐次実行・リトライ・キャッシュ（計画書11章の方針）を必ず通す
