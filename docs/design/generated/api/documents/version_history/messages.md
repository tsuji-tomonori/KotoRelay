<!-- 実装から生成。直接編集しない。入力SHA256: 4c18ae62a9b9de513581947abfc60f1ec45b9f631019a142a812724b4695a84b -->

# 担当文書の版履歴 — ログメッセージ

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## API

| 項目 | 値 |
| --- | --- |
| operation | version_history |
| endpoint | GET /api/documents/{document_id}/history |
| router | backend/src/kotorelay/operations/documents/router.py |


## 生成・検証方針

共通HTTP middlewareのlogger呼出しと実行時LOG_MESSAGESを読み取ります。HTTPエラーメッセージをログとして置換しません。

## メッセージ一覧

| id | message_id | ログ概要 |
| --- | --- | --- |
| M001 | KR_REQUEST | HTTP応答時の相関ID・メソッド・ステータス |


## ログ詳細

### `M001` `KR_REQUEST`

| 項目 | 内容 |
| --- | --- |
| level | INFO |
| テンプレート | request_id=%s method=%s status=%s |
| 条件 | HTTP応答生成時 |
| 場所 | backend/src/kotorelay/main.py:security_headers |
| 運用対応 | 5xxはrequest_idから照合。409は再読込後に再試行。 |

#### 出力項目

| 出力項目 | 型 | マスク規則 |
| --- | --- | --- |
| request_id | UUID文字列 | 相関用ID |
| method | str | HTTPメソッドのみ |
| status | int | HTTPコードのみ |


## strict検証で要求する項目

LOG_MESSAGESとlogger呼出しが実装に存在すること。本文・JWT・OCR本文をログに含めないこと。lazunex固有のloggerラッパーやWARNING以上の運用規則は、本実装の規則として転記しません。