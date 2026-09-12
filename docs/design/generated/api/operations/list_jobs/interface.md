<!-- 実装から生成。直接編集しない。入力SHA256: 4c18ae62a9b9de513581947abfc60f1ec45b9f631019a142a812724b4695a84b -->

# 反映ジョブと失敗理由を確認 — インターフェース

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## Headers

該当する入力はありません。

認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


## Path Parameters

該当する入力はありません。

## Query Parameters

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| details | boolean | 任意 | OpenAPIの型制約に従う | {"type": "boolean", "default": false, "title": "Details"} |


## Data

リクエスト本文はありません。

## Responses

| Status | 説明 | Media type |
| --- | --- | --- |
| 200 | Successful Response | application/json |
| 422 | Validation Error | application/json |

##### `200` Successful Response

型: `array<object>`。定義: `{"type": "array", "items": {"type": "object", "additionalProperties": true}, "title": "Response List Jobs"}`


##### `422` Validation Error

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| detail | array<ValidationError> | 任意 | 型定義に説明なし | {} |
| detail[].loc | array<string &#124; integer> | 必須 | 型定義に説明なし | {} |
| detail[].msg | string | 必須 | 型定義に説明なし | {} |
| detail[].type | string | 必須 | 型定義に説明なし | {} |
| detail[].input | object（追加項目はスキーマ参照） | 任意 | 型定義に説明なし | {} |
| detail[].ctx | object | 任意 | 型定義に説明なし | {} |


## Samples

このAPIのOpenAPIにHTTP応答exampleは定義されていません。架空の成功応答は生成しません。入力形式は上記のData、実際の入力と期待値は単体テスト詳細を参照してください。