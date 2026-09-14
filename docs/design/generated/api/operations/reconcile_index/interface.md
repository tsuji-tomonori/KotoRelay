<!-- 実装から生成。直接編集しない。入力SHA256: dc958b6e6841a9f29856eb932e8271e37a6d4416a3266624301c411c89949f81 -->

# 正本と索引の不一致を確認 — インターフェース

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

型: `array<object>`。定義: `{"items": {"additionalProperties": {"type": "string"}, "type": "object"}, "type": "array", "title": "Response Reconcile Index"}`


## Samples

### 認証情報がない要求の拒否

認証情報なしのHTTP要求と不変項目を実テストで確認します。

```json
{
  "name": "認証情報がない要求の拒否",
  "method": "GET",
  "path": "/api/operations/reconcile",
  "expected_status": 401,
  "expected_fields": {
    "code": "unauthenticated"
  }
}
```