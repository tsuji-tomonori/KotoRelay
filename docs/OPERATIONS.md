# ローカル実行・AWS運用

## ローカル

Node.js 24、Python 3.12、uv、Docker Compose v2が必要です。`uv sync --frozen`、`npm ci`後、`docker compose up -d --build --wait`で http://localhost:4321 を開きます。APIは http://localhost:58000/docs、PostgreSQLはlocalhost:55432です。ローカル専用の架空利用者をログイン画面から選べます。

文書を執筆者で作成・保存・申請し、審査者で承認します。運用担当の「検索反映」から配送するか、`docker compose --profile worker up -d worker`で自動配送を有効にします。E2Eは配送時点を明確に検証するためworkerを起動せず、各ケースが対象ジョブを処理します。

`uv run python tools/project/verify.py`は静的解析、整形、型、実PostgreSQL結合、単体、CDK、Compose E2Eを実行して品質サイトを作成します。`python3 -m http.server 4173 --directory artifacts/site`で確認できます。既存の結果に失敗があれば公開しても成功扱いにしません。

## AWS構築

AWSアカウントに対するデプロイはまだ実行していません。以下は利用者が課金と構築先を確認して実行する手順です。

1. `aws login`等で認証し、`aws sts get-caller-identity`で対象を確認する。ap-northeast-1でDSQL、S3 Vectors、Bedrock Nova Lite/Titanの利用可否とクォータを確認する。
2. `uv sync --frozen`、`npm ci`、`npm run build`を実行する。
3. `npx cdk bootstrap`、`npx cdk synth`、`npx cdk diff`を実行し、テンプレートを確認して`npx cdk deploy --outputs-file .workspace/aws-outputs.json`を実行する。CDK CLIは`npx cdk`で呼び出してもよい。
4. CDKのDatabaseEndpointを`KOTORELAY_DSQL_HOST`、`KOTORELAY_MODE=aws`、`KOTORELAY_DSQL_USER=admin`として、新規空DBに`uv run python -m kotorelay.migrate`を実行する。`PYTHONPATH=backend/src`が必要。DDLは一つずつ独立transactionで適用する。途中失敗時は適用済み一覧を照合し、未適用のDDLだけを再開する。
5. admin接続で`CREATE ROLE kotorelay_app WITH LOGIN`、`GRANT USAGE ON SCHEMA public TO kotorelay_app`、`GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO kotorelay_app`、`AWS IAM GRANT kotorelay_app TO '<AppRoleArn>'`を実行する。実行ロールにはDbConnectAdminを付与しない。
6. Cognitoに自己登録なしで利用者を作成する。users.subjectにCognitoのsubを登録し、組織・部署・所属を初期登録する。service-workerというsubjectのoperatorも登録する。ローカルseedはAWS実行を拒否する。利用者・部署・権限は組織内のUUIDと複合参照で登録する。
7. `aws s3 sync frontend/dist s3://<FrontendBucket>`で静的ファイルを配置する。CloudFrontのWebsite出力で開く。現在のAWSログイン画面はCognitoのaccess token入力方式。CognitoのSRP対応クライアントで取得した有効なaccess tokenを入力する。Hosted UIはこのサンプルに含めない。
8. 架空の文書で執筆→別人承認→worker配送→実ベクトル読戻し→Bedrock画像付き回答→公開停止後の失効を確認する。実データを投入する前に、AWS版の疎通結果を追加記録する。

DSQLの接続は公式Python connectorでIAMトークンを発行し、TLS証明書をverify-fullで検証します。DSQLは2026-08-27から外部キーをサポートしています。古い資料の「外部キー非対応」は使用していません。[AWS発表](https://aws.amazon.com/about-aws/whats-new/2026/08/aurora-dsql-foreign-key-constraints/)

## 費用

常設サーバー、NAT Gateway、ALB、OpenSearch Serverless OCU、独自ドメイン、顧客管理KMS鍵、Provisioned Concurrencyは作成しません。無料枠内での試行を意図しますが、月額料金の完全なゼロは保証できません。DSQLの処理・ストレージ、S3、S3 Vectors、Bedrock、CloudFront、CloudWatch Logs、Lambda、EventBridge、CDKのECR保存等は従量料金の対象です。

- Cost ExplorerでProject=kotorelay / CostCenter=sampleを有効化し、サービス別・日別に確認する。タグ反映には遅延がある。
- APIと配送workerは別のLambdaなので、Lambdaメトリクスを関数別に確認できる。Bedrockはモデル別の入力・出力トークンと呼出数、S3 Vectorsは保存量とquery数、DSQLはDPUと保存量を確認する。質問本文や画像をログへ出力しない。
- 質問は利用者ごと1日100件、モデル画像5件、添付10件、1画像3MiB/20MP、1文書最大300チャンク。API同時実行3、worker同時実行1。失敗配送は最大5回。
- S3アクセスログ、CloudFrontアクセスログ、WAF、高度なCognito脅威保護は費用理由を付けた対象限定cdk-nag例外。TLS、非公開バケット、JWT、最小権限の基本的な検査は継続する。

## バックアップと復旧

DSQLはAWS Backupのオンデマンドバックアップで保護できる。保存量に応じて追加費用が発生するため、このサンプルでは自動バックアップplanを常設しない。[DSQLバックアップと復旧](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/backup-aurora-dsql.html)

1. 運用時間帯を決め、organizations.suspendedをtrueにしてアプリの認証を停止し、API/workerの進行中処理が終了したことを確認する。
2. DSQLの復旧ポイントを取得し、同じ時点のContentBucket内容ハッシュオブジェクトを別の非公開バックアップ先にコピーする。DBの版・承認・所属・監査・idempotency・outboxを一体として保護する。日時、組織revision、S3オブジェクト一覧とSHA256を記録する。暗号化と閲覧権限を維持する。
3. 別の新規DSQLへ復元する。古い公開権限が復活しないよう、元環境の復旧ポイント以降の権限剥奪・公開停止・削除監査を照合するまでsuspended=trueを維持する。Cognitoのsubとusersの対応を照合する。
4. S3の文書本文・画像・OCRのハッシュを確認する。S3 Vectorsは正本ではないため、新しい空の索引に再構築する。承認版に対応するoutboxだけを配送し、件数と読戻し、manifestと断片SHA256を確認する。古い索引をそのまま公開しない。
5. 境界テスト（他部署の404、旧版拒否、公開停止文書の回答保留、画像/OCRの拒否）と監査件数を確認した後にsuspendedを解除する。

ローカルでは停止中に`docker compose exec -T db pg_dump -U kotorelay -d kotorelay`を権限制限したファイルへ保存し、objects volumeと同じ時点でバックアップする。復元先は新規DB・新規volumeを使用する。DBだけを復元して画像の整合性を成功扱いにしない。

## 削除と再開

削除操作は即時に文書と根拠の配信を停止し、outboxにpurgeを記録する。既定7日の保持期間後に本文・画像・OCR・ベクトル・その文書を使った回答実体を回収する。他の有効文書で同じ内容ハッシュを使っている場合は実体を維持する。DB断片/OCRの削除は100行単位で再開可能。版・審査・監査メタデータは監査用に残す。検索反映画面で失敗理由と試行数、不一致を確認できる。

サンプルは単一組織・小規模データを想定する。全組織revisionのCASは認可変更と回答確定の競合を安全側で検出する一方、高負荷では競合が増える。大規模展開では文書/所属単位の競合制御、検索候補のページング、長時間ジョブの分割を追加し、負荷測定する。


## UI改訂の互換性

画像の代替テキストと説明文は配置JSON、領域IDと訂正の由来はOCR JSONに追加しています。既存の承認版とオブジェクトのハッシュは書き換えません。旧OCRの領域IDはrun IDと配列位置から読取時に安定して補い、訂正すると新しいrunになります。挿入位置はUnicodeコードポイント数です。本文先頭の空白と末尾改行も保存します。

文書一覧は`page=true`で`items/has_next`と版・審査・反映概要を取得します。省略時は従来の配列形式です。部署フィルターは`department_id`、削除APIは`reason`が必須になりました。利用部署の異なる質問を既存会話へ追加する要求は409となるため、新しい会話を開始します。今回の永続情報は既存JSON列と監査列を使用し、DDLの変更はありません。

自動試験は実ブラウザのフォーカス・キーボード・320〜1440px・200%文字拡大と意味構造を対象にします。実スクリーンリーダーでの読み上げ品質とWCAG全項目への適合は未検証です。

保存系APIはDBのcommitが完了してから成功応答を返す。FastAPIの依存を`scope="function"`とし、commit時の競合も409として利用者へ返す。応答送信時の別接続からの可視性と、commit失敗時のrollbackを実PostgreSQLで検証する。参照：[FastAPIのyield依存とscope](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/#early-exit-and-scope)。
