<!-- 実装から生成。直接編集しない。入力SHA256: 0ce2ee5ffefd1f44a0c3da213ceff59dfb82649c9add5715e204664ffd05fd84 -->

# 最新承認版の根拠で回答 — ログメッセージ

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## API

| 項目 | 値 |
| --- | --- |
| operation | ask_question |
| endpoint | POST /api/chat |


## 生成・検証方針

lazunexのops_loggerと同じく、独自型のcontext、ログID、例外型、応答、確認・復旧手順を必須にします。実行時catalogと実際のops_logger呼出しから生成します。通常アクセスのINFO KR_REQUESTは相関ID・メソッド・statusだけを記録します。

## メッセージ一覧

| message_id | level | ログ概要 |
| --- | --- | --- |
| KR_EVIDENCE_REJECTED | WARNING | 整合性を確認できない回答根拠を除外しました。 |
| KR_HTTP_FAILED | ERROR | 処理を完了できずエラー応答を返しました。 |
| KR_HTTP_REJECTED | WARNING | 業務条件または入力検証によりリクエストを拒否しました。 |
| KR_MODEL_FAILED | ERROR | 回答モデルの呼出しが失敗しました。 |


## ログ詳細

### `KR_EVIDENCE_REJECTED`

| 項目 | 内容 |
| --- | --- |
| level | WARNING |
| メッセージ | 整合性を確認できない回答根拠を除外しました。 |
| 例外・出力条件 | 根拠の読込み・検証でProblemまたはValueErrorを捕捉した場合。 |
| 返すレスポンス | HTTPエラーを直ちに返さず根拠を除外して継続。残る有効根拠により回答を返すかstatus=held、履歴はstatus=hidden。 |
| 呼出し位置 | backend/src/kotorelay/operations/chat/ask_question/router.py:70, backend/src/kotorelay/operations/chat/shared/functions.py:69 |
| 確認手順 | request_idと例外型から版・権限・実体の整合性を確認する。 |
| 復旧手順 | 公開版と索引を照合し、必要なら再索引する。 |


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


### `KR_MODEL_FAILED`

| 項目 | 内容 |
| --- | --- |
| level | ERROR |
| メッセージ | 回答モデルの呼出しが失敗しました。 |
| 例外・出力条件 | 回答生成中にBotoCoreError / ClientError / TimeoutErrorを捕捉した場合。 |
| 返すレスポンス | 後続の再認可と保存が成功すればHTTP 200、AnswerView.status=failed、answer=現在利用できる根拠が不足しているため、回答を保留しました。 |
| 呼出し位置 | backend/src/kotorelay/operations/chat/ask_question/router.py:126 |
| 確認手順 | request_idと例外型からモデルの稼働と呼出し権限を確認する。 |
| 復旧手順 | 依存先の復旧後に新しい質問として再実行する。 |


### 例外からHTTPエラー応答への対応

以下は例外が内部で処理されずHTTP境界に到達した場合の応答です。内部で捕捉して継続する経路はシーケンスのcatchと上記ログ別の継続結果を参照してください。

| 例外 | HTTP | code | message | ログID |
| --- | --- | --- | --- | --- |
| Problem | 401 | unauthenticated | ログインが必要です。 | KR_HTTP_REJECTED |
| Problem | 403 | forbidden | この操作は許可されていません。 | KR_HTTP_REJECTED |
| Problem | 404 | not_found | 対象を利用できません。 | KR_HTTP_REJECTED |
| Problem | 409 | conflict | 他の操作で更新されました。最新の状態を確認してください。 | KR_HTTP_REJECTED |
| psycopg.Error | 409 | conflict | 競合しました。再読込してください。 | KR_HTTP_REJECTED |
| Problem | 409 | conversation_department | 利用部署を変更する場合は新しい会話を開始してください。 | KR_HTTP_REJECTED |
| Problem | 409 | idempotency_conflict | 同じ操作IDが異なる内容で使用されています。 | KR_HTTP_REJECTED |
| RequestValidationError | 422 | invalid_input | 入力形式を確認してください。 | KR_HTTP_REJECTED |
| Problem | 429 | limit | 利用上限に達しました。 | KR_HTTP_REJECTED |
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