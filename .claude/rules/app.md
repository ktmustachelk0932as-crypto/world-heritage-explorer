---
paths:
  - "app/**"
---

# app/ のルール

- `st.*` の使用は `app/` 配下に閉じ込める（`core/` に持ち込まない）
- アプリは `data/processed/` のみを読む。`data/raw/` を直接参照しない
