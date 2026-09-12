# サンプル実装の設計判断

2026-09-12の実装依頼を、ZIPの89件を実装する指示として扱う。ZIP中の「今回実装しない」は要件資料を作成した当時の範囲であり、今回の実装を止める条件ではない。元資料と提案モデルは保存し、実装由来の生成設計は別ディレクトリへ置く。

- フロントはAstro + React + TypeScript。Astralの指定は「等モダンな技術」の範囲でAstroと解釈する。
- Python + FastAPI + uv、AWS CDK Python。クラウド正本はAurora DSQL、ローカルはPostgreSQL。
- 自己承認を禁止する。一般閲覧は最新承認版だけ。部署リーダーと執筆・審査権限を分離する。
- 添付はPNG/JPEG、3MiB、20メガピクセル、1文書10枚。OCRは日本語対応Tesseract、訂正・確認後に申請する。モデルへの画像上限は5枚。超過した画像根拠は全体を除外する。
- ローカルのRAGは決定的な検索・抜粋方式を明示する。実Bedrockの意味検索・画像入力検証の代用とは表示しない。
- 保存時に明示的な版番号による競合検出。確定版は変更不能。公開判定と回答確定は認可リビジョンを使ったOCCで直列化する。
- 集計はイベントの一意IDから都度計算し、日本時間、集計時刻と対象期間を表示する。
- 固定の待機計算費を持つEC2/ECS/NAT/ALB/OpenSearch Serverless、Provisioned Concurrency、カスタマー管理KMSキーは採用しない。DSQL、S3、Bedrock、API等の利用・保存に応じた料金は発生し得る。AWSで一律に月額0円を保証する構成ではない。
- AWSデプロイはこの依頼の実装・CDK検証と区別する。実DSQL接続・実Bedrock・クラウド復旧試験は実行した証拠が揃うまで未検証とする。

標準参照: https://github.com/tsuji-tomonori/dev-standard/tree/d61eb54cd52bd97391f369a85b07324abf37a829

料金根拠: https://aws.amazon.com/rds/aurora/dsql/pricing/ 、 https://docs.aws.amazon.com/aurora-dsql/latest/userguide/billing-metering.html


画像はAPI Gateway/Lambdaのbase64転送とBedrock Converseの上限に収まるよう、入力・正規化後とも3MiB、各辺8000px以下とする。[Converseの公式制限](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Message.html)

S3 Vectorsの接続情報はIndexArnに統一する。CloudFormationのVectorBucket RefはARNを返すため、バケット名としてSDKへ渡さない。[CloudFormationの返却値](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-s3vectors-vectorbucket.html)
