# world-heritage-explorer

世界遺産の分布・登録動向を可視化する Streamlit アプリです。
Wikidata（SPARQL）から構築した世界遺産データセットを元に、インタラクティブ地図・国別サマリー・年次登録推移を表示します。

## 機能

アプリは 3 ページ構成です（`app/main.py` の `st.navigation` でルーティング）。

| ページ | ファイル | 内容 |
| --- | --- | --- |
| 🗺️ 地図 | `app/views/map.py` | folium + MarkerCluster による世界地図。分類（文化／自然／複合）ごとにマーカー色を分け、マーカークリックまたは名称検索で右側に詳細パネルを表示 |
| 🌐 国別サマリー | `app/views/country.py` | 国ごとの登録件数と分類内訳を Plotly の棒グラフで表示。国を選ぶと内訳の詳細を表示 |
| 📈 登録推移 | `app/views/trend.py` | 年次の登録件数を分類別の積み上げエリアチャートで表示。全世界／国別を切替可能 |

詳細パネルには次を表示します。

- 名称・登録年・国・分類・登録基準（(i)〜(x) の日本語説明付き）
- Wikimedia Commons の代表画像とライセンス表記（作者・ライセンス名・出典ページへのリンク）

国名は ISO コードから和名へ、遺産名は Wikidata の日本語ラベル（無い場合は同梱の対訳表）で日本語表示します。

## 技術スタック

| 用途 | ライブラリ |
| --- | --- |
| 言語 | Python 3.11+ |
| パッケージ管理 | uv（`pyproject.toml` / `uv.lock`） |
| UI | Streamlit 1.62 |
| 地図 | folium 0.20 / streamlit-folium 0.27（タイル: OpenStreetMap） |
| グラフ | Plotly 7 |
| データ処理 | pandas 3 / pyarrow（parquet） |
| 外部 API | requests / tenacity（リトライ） |
| 開発ツール | ruff（format / lint）/ pytest |

## ディレクトリ構成

```
.
├── app/                        # Streamlit UI（st.* はこの配下のみ）
│   ├── main.py                 # エントリーポイント。ページのルーティングのみ
│   ├── views/
│   │   ├── map.py              # 地図ページ
│   │   ├── country.py          # 国別サマリーページ
│   │   └── trend.py            # 登録推移ページ
│   └── components/
│       ├── map_view.py         # folium 地図の構築、マーカー色・分類ラベル定義
│       ├── detail_panel.py     # 詳細情報パネル（テキスト＋代表画像＋ライセンス表記）
│       ├── country_summary.py  # 国別グラフ（Plotly）
│       ├── trend_chart.py      # 年次推移グラフ（Plotly）
│       └── page_common.py      # 共通のデータ読み込み（st.cache_data）・注記表示
├── core/                       # ビジネスロジック（Streamlit 非依存）
│   ├── data_loader.py          # parquet / サンプル CSV の読み込み・検証・和名化
│   ├── aggregations.py         # 国別集計・年次集計
│   ├── criteria.py             # 登録基準 (i)〜(x) の日本語説明
│   ├── country_names.py        # ISO 3166-1 alpha-2 → 国名（和名）
│   ├── site_names_ja.py        # 日本語ラベルが無い遺産の和名対訳
│   ├── image_fetcher.py        # Wikimedia Commons API から画像 URL・ライセンス取得
│   ├── cache_manager.py        # 画像情報の SQLite キャッシュ
│   ├── user_agent.py           # Wikimedia API 向け User-Agent の組み立て
│   └── env.py                  # .env の最小ローダ
├── scripts/                    # データ構築バッチ
│   ├── fetch_raw_data.py       # Wikidata SPARQL → data/raw/
│   ├── build_dataset.py        # data/raw/ → data/processed/heritage_sites.parquet
│   └── prefetch_images.py      # 代表画像を一括取得 → キャッシュ DB + heritage_images.parquet
├── data/
│   ├── raw/                    # SPARQL 結果 JSON（Git 管理外）
│   ├── processed/              # アプリが読む整形済みデータ（コミット対象）
│   │   ├── heritage_sites.parquet
│   │   ├── heritage_images.parquet
│   │   └── heritage_sites_sample.csv   # parquet が無いときのフォールバック
│   └── cache/                  # image_cache.sqlite（Git 管理外）
├── tests/                      # pytest（core / app コンポーネント / scripts）
├── .streamlit/config.toml      # テーマ設定
├── .claude/                    # Claude Code 用ルール・スキル
├── CLAUDE.md
├── pyproject.toml
└── uv.lock
```

## セットアップ

前提: Python 3.11 以上、[uv](https://docs.astral.sh/uv/)（推奨）

```bash
git clone https://github.com/ktmustachelk0932as-crypto/world-heritage-explorer.git
cd world-heritage-explorer
uv sync
```

uv を使わない場合:

```bash
python -m venv .venv
source .venv/bin/activate
pip install streamlit streamlit-folium folium plotly pandas requests tenacity pyarrow
pip install ruff pytest   # 開発用
```

### 環境変数（任意）

Wikimedia API へアクセスする際の User-Agent に含める連絡先を設定できます（Wikimedia の利用規約で推奨）。
未設定でも動作しますが、警告ログが出ます。プロジェクト直下に `.env` を作成してください（Git 管理外）。

```dotenv
WIKIMEDIA_CONTACT_EMAIL=https://github.com/<your-account>/world-heritage-explorer
```

Streamlit Community Cloud にデプロイする場合は、Secrets に同名のキーを設定します。

## アプリの起動方法

```bash
# uv 経由
uv run streamlit run app/main.py

# venv を有効化している場合
streamlit run app/main.py
```

- 起動するとブラウザが自動で開きます。開かない場合は <http://localhost:8501> にアクセスしてください
- ポートを変える場合: `streamlit run app/main.py --server.port 8502`
- 起動直後は「地図」ページが表示され、サイドバーから「国別サマリー」「登録推移」へ切り替えられます
- 整形済みデータ `data/processed/heritage_sites.parquet` を同梱しているため、データ取得スクリプトを実行しなくてもそのまま動作します（parquet が無い場合は `heritage_sites_sample.csv` にフォールバック）
- 停止はターミナルで `Ctrl+C`

## データパイプライン

UNESCO 公式サイト（whc.unesco.org）は Bot 対策により自動取得できず、UNESCO DataHub にも座標付きの一覧が無いため、
Wikidata の SPARQL エンドポイントから「世界遺産（Q9259）」の指定を受けた項目を取得しています。

データを更新するときは次の順に実行します（各ステップが失敗したらそこで中断）。

```bash
python3 scripts/fetch_raw_data.py     # 1. SPARQL 結果を data/raw/wikidata_world_heritage_sites.json へ保存
python3 scripts/build_dataset.py      # 2. 構成資産を WHC 参照番号で統合し data/processed/heritage_sites.parquet を生成
python3 scripts/prefetch_images.py    # 3. 全遺産の代表画像 URL・ライセンスを取得（逐次アクセスのため時間がかかる）
pytest                                # 4. 検証
```

`prefetch_images.py` のオプション:

- `--limit N` … 処理件数の上限（動作確認用）
- `--force` … 取得済みのものも再取得する

画像取得は Wikimedia Commons API を `core/image_fetcher.py` 経由で逐次呼び出し、tenacity によるリトライと
SQLite キャッシュ（`data/cache/image_cache.sqlite`）を通します。CC0 / CC BY 系 / パブリックドメイン以外の
ライセンスの画像は除外します。地図ページで画像スナップショットに無い遺産を開いた場合のみ、その場で 1 件取得します。

Claude Code を使っている場合は `/update-data` スキルで上記を一括実行できます。

## データセットのスキーマ

### `data/processed/heritage_sites.parquet`

| 列 | 型 | 内容 |
| --- | --- | --- |
| `site_id` | int | WHC 参照番号 |
| `name` | str | 遺産名（日本語ラベル優先） |
| `country` | str | 国名（英語。表示時に和名へ変換） |
| `iso_code` | str | ISO 3166-1 alpha-2 |
| `category` | str | `Cultural` / `Natural` / `Mixed` |
| `date_inscribed` | int | 初回登録年 |
| `latitude` / `longitude` | float | 代表座標 |
| `criteria` | str | 登録基準（例: `(vii)(viii)(ix)(x)`） |
| `wikidata_qid` | str | Wikidata の QID |
| `image_filename` | str | Commons の代表画像ファイル名（P18） |

### `data/processed/heritage_images.parquet`

| 列 | 型 | 内容 |
| --- | --- | --- |
| `site_id` | int | WHC 参照番号 |
| `image_url` | str | 画像 URL |
| `source_page_url` | str | Commons のファイルページ URL |
| `license_short_name` / `license_url` | str | ライセンス名・URL |
| `artist` | str | 作者（HTML 除去済み） |
| `attribution_required` | bool | 帰属表示が必要か |
| `retrieved_at` | str | 取得日時（ISO 8601, UTC） |

### 注意事項

- 登録年は初回登録年のみで、後年の範囲拡張・変更は反映していません
- 座標・分類は Wikidata の情報を元に算出しており、UNESCO 公式データと差異がある場合があります
- 座標が欠損・範囲外の行、分類が不明な行は読み込み時に除外されます

## テスト・Lint

```bash
pytest                 # 全テスト
ruff format .          # フォーマット
ruff check .           # Lint
```

テストは `core/` のロジック、`app/components/` の描画関数、`scripts/build_dataset.py` の変換処理、
ページナビゲーションを対象にしています。

## アーキテクチャ方針

- `core/` は Streamlit に依存させない（`st.*` は `app/` 配下のみ）
- アプリは `data/processed/` のみを読み、`data/raw/` を直接参照しない
- Wikimedia API の呼び出しは `core/image_fetcher.py` 経由に限定し、逐次実行・リトライ・キャッシュを必ず通す
- 外部 API リクエストにはタイムアウトを明示する
- エラーは握りつぶさず、ログに記録した上でフォールバック表示に切り替える
- 型ヒントを付ける

## データの出典

- 世界遺産データ: [Wikidata](https://www.wikidata.org/)（CC0）
- 代表画像: [Wikimedia Commons](https://commons.wikimedia.org/)（各画像のライセンスをアプリ内に表示）
- 地図タイル: © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors
