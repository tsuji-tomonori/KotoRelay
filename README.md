# KotoRelay（コトリレー）

承認した知識を、人とAIへつなぐ文書管理サンプルです。Markdownの執筆、画像・OCRを含む版の承認、部署ごとの共有、現行権限で保護した根拠付きチャットを提供します。

[設計と品質ポータル](https://tsuji-tomonori.github.io/KotoRelay/) · [運用手順](docs/OPERATIONS.md) · [要件](docs/requirements/REQUIREMENTS.md) · [API設計](docs/design/generated/API.md) · [設計判断](docs/decisions/IMPLEMENTATION.md) · [UI改訂方針](docs/planning/UI-REVISION.md)

```bash
# Node.js 24 / Python 3.12 / uv / Docker Compose v2
uv sync --frozen
npm ci
docker compose up -d --build --wait
```

http://localhost:4321 を開き、執筆者で文書を作成・保存・申請、審査者で承認、運用担当で検索反映します。自動配送は `docker compose --profile worker up -d worker` で起動できます。ローカルの回答は資料の抜粋です。AWSではBedrock Nova LiteとTitan embeddings、S3 Vectorsを使います。

- **フロント:** TypeScript / Astro / React。安全なMarkdown、画像の挿入位置、OCR領域、入力保持、部署管理。
- **バックエンド:** Python / FastAPI / uv。PostgreSQL、AWSではIAM認証のAurora DSQL。SQL正本から型付きqueryを生成。
- **インフラ:** Python CDK。Lambdaコンテナ、API Gateway、Cognito、S3、CloudFront、DSQL、S3 Vectors、EventBridge。
- **検証:** Ruff、mypy、SQLFluff、ESLint、Prettier、Astro/TypeScript、pytest、Vitest、Playwright、cdk-nag、CDKアサーションとスナップショット。

```bash
# 開発標準の固定Quintランタイムを準備
python3 tools/quintflow.py setup
# 静的解析・単体・実DB結合・CDK・Compose E2E・SPA生成
uv run python tools/project/verify.py
# ポータルの検索・図・画像拡大・モバイルを確認
npx playwright test --config e2e/portal.config.ts
# 品質SPAをローカルで閲覧
python3 -m http.server 4173 --directory artifacts/site
```

UIは提供デザインに沿った文字・配色・メニューと、OCR領域編集、未保存確認、引用版の更新案内、公開設定の明示保存を備えます。原資料・ZIP・一時ログを置く `.workspace/` はGit管理対象外です。

閾値はC0相当95%、C1相当90%。実行文・行・分岐を区別して分母分子を公開します。E2EのGiven/When/ThenごとにPNGを記録し、必要なDB状態を添付します。未実行・失敗・再試行を成功へ読み替えません。

要件は `spec/requirements/requirements.qnt` が正本です。変更後は `python3 tools/quintflow.py generate` を実行します。現在設計は `uv run python tools/project/design.py`、型付きSQLは `uv run python tools/project/queries.py` で生成し、それぞれ `--check` で欠落・変更を検出します。

AWSへの実デプロイと実DSQL/Bedrockの疎通は未実行です。常設サーバー等の待機計算固定費を避けた構成ですが、AWSの利用量・保存量による料金は発生します。構築・認証・バックアップ・復旧・cdk-nag除外理由は運用手順を参照してください。

設計書の章構成・API階層・CRUD図は[生成設計の構成方針](docs/planning/DOCUMENT-STRUCTURE.md)に従います。
