<!-- 実装から生成。直接編集しない。入力SHA256: f473ec4902a9e7cc973e702d4fbb05a99ce8c26a324da9a1f4592aab94dbd60c -->

# 死活確認 — ログメッセージ

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## API

| 項目 | 値 |
| --- | --- |
| operation | health |
| endpoint | GET /api/health |


## 生成・検証方針

lazunexのops_loggerと同じく、独自型のcontext、ログID、例外型、応答、確認・復旧手順を必須にします。実行時catalogと実際のops_logger呼出しから生成します。通常アクセスのINFO KR_REQUESTは相関ID・メソッド・statusだけを記録します。

## メッセージ一覧

| message_id | level | ログ概要 |
| --- | --- | --- |


## ログ詳細

### 例外からHTTPエラー応答への対応

以下は例外が内部で処理されずHTTP境界に到達した場合の応答です。内部で捕捉して継続する経路はシーケンスのcatchと上記ログ別の継続結果を参照してください。

| 例外 | HTTP | code | message | ログID |
| --- | --- | --- | --- | --- |


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