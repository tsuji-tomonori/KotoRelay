<!-- 実装から生成。直接編集しない。入力SHA256: 31de213f242d3d7bf0d4f5957d4ef327aaacb2267a973d8e0adce1f1531ac7e1 -->

# 本人と現在の所属権限を取得 — インターフェース

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## Headers

該当する入力はありません。

認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


## Path Parameters

該当する入力はありません。

## Query Parameters

該当する入力はありません。

## Data

リクエスト本文はありません。

## Responses

| Status | 説明 | Media type |
| --- | --- | --- |
| 200 | Successful Response | application/json |

##### `200` Successful Response

型: `object`。定義: `{"additionalProperties": true, "type": "object", "title": "Response Get Identity"}`


## Samples

このAPIのOpenAPIにHTTP応答exampleは定義されていません。架空の成功応答は生成しません。入力形式は上記のData、実際の入力と期待値は単体テスト詳細を参照してください。