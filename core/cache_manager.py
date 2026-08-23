"""SQLiteキャッシュ（data/cache/image_cache.sqlite）の読み書き。

site_id, image_url, ライセンス・作者情報, retrieved_at を永続化し、
同一遺産へのAPI再リクエストを防止する。
"""
