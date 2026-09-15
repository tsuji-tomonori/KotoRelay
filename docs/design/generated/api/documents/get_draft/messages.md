<!-- 実装から生成。直接編集しない。入力SHA256: f473ec4902a9e7cc973e702d4fbb05a99ce8c26a324da9a1f4592aab94dbd60c -->

# 下書きを取得 — ログメッセージ

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## API

| 項目 | 値 |
| --- | --- |
| operation | get_draft |
| endpoint | GET /api/documents/{document_id}/draft |


## 生成・検証方針

lazunexのops_loggerと同じく、独自型のcontext、ログID、例外型、応答、確認・復旧手順を必須にします。実行時catalogと実際のops_logger呼出しから生成します。通常アクセスのINFO KR_REQUESTは相関ID・メソッド・statusだけを記録します。

## メッセージ一覧

| message_id | level | ログ概要 |
| --- | --- | --- |
| KR_HTTP_FAILED | ERROR | 処理を完了できずエラー応答を返しました。 |
| KR_HTTP_REJECTED | WARNING | 業務条件または入力検証によりリクエストを拒否しました。 |


## ログ詳細

### `KR_HTTP_FAILED`

| 項目 | 内容 |
| --- | --- |
| level | ERROR |
| メッセージ | 処理を完了できずエラー応答を返しました。 |
| 例外・出力条件 | Problemの5xx、競合以外のpsycopg.Error、外部サービス例外をHTTP境界で捕捉した場合。 |
| 返すレスポンス | HTTP status / code / messageはcontextの応答と一致。request_idは相関ID。 |
| 呼出し位置 | backend/src/kotorelay/main.py:error_response |
| 確認手順 | request_idから例外型と応答コードを調べ、DB接続・実体整合性・外部サービス稼働を確認する。 |
| 復旧手順 | 依存先を復旧し、保存済み状態を確認して同じ操作IDで再試行する。 |


### `KR_HTTP_REJECTED`

| 項目 | 内容 |
| --- | --- |
| level | WARNING |
| メッセージ | 業務条件または入力検証によりリクエストを拒否しました。 |
| 例外・出力条件 | Problemの4xx、RequestValidationError、DBの競合例外をHTTP境界で捕捉した場合。 |
| 返すレスポンス | HTTP status / code / messageはcontextの応答と一致。request_idは相関ID。 |
| 呼出し位置 | backend/src/kotorelay/main.py:error_response |
| 確認手順 | request_idで検索し、例外型・code・HTTP statusを確認する。 |
| 復旧手順 | 401は再認証、403/404は権限、409は再読込、422は入力、429は時間を置いて再試行する。 |


### 例外からHTTPエラー応答への対応

以下は例外が内部で処理されずHTTP境界に到達した場合の応答です。内部で捕捉して継続する経路はシーケンスのcatchと上記ログ別の継続結果を参照してください。

| 例外 | HTTP | code | message | ログID |
| --- | --- | --- | --- | --- |
| Problem | 401 | unauthenticated | ログインが必要です。 | KR_HTTP_REJECTED |
| Problem | 404 | not_found | 対象を利用できません。 | KR_HTTP_REJECTED |
| psycopg.Error | 409 | conflict | 競合しました。再読込してください。 | KR_HTTP_REJECTED |
| RequestValidationError | 422 | invalid_input | 入力形式を確認してください。 | KR_HTTP_REJECTED |
| psycopg.Error / BotoCoreError / ClientError / OSError / TimeoutError | 503 | unavailable | 一時的に利用できません。 | KR_HTTP_FAILED |


### 型付き出力項目

| 項目 | 型 | 内容 |
| --- | --- | --- |
| request_id | uuid.UUID &#124; None | HTTP要求との相関ID。workerではnull。 |
| exception_type | str | 捕捉した例外の型名。 |
| status | int &#124; None | 確定したHTTPエラーのstatus。継続処理ではnull。 |
| code | str &#124; None | 安全なHTTP応答またはジョブの失敗コード。その他の継続処理ではnull。 |
| message | str | HTTP応答の安全なメッセージ、またはcatalogの継続結果。 |


## strict検証で要求する項目

型・catalogの未登録ID、未知context項目、level不一致を拒否します。例外の生メッセージ、本文、JWT、OCR原文は渡しません。HTTPエラーにはrequest_idを付け、同じIDのログと照合します。