<!-- 実装から生成。直接編集しない。入力SHA256: 065f3a0aaa159ee25b4b54797ae13bebd5e0deb08cdd00f2becc4afbe26e1319 -->

# 現行認可で会話履歴を再表示 — インターフェース

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## Headers

該当する入力はありません。

認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


## Path Parameters

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| conversation_id | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "uuid", "title": "Conversation Id"} |


## Query Parameters

該当する入力はありません。

## Data

リクエスト本文はありません。

## Responses

| Status | 説明 | Media type |
| --- | --- | --- |
| 200 | Successful Response | application/json |
| 422 | Validation Error | application/json |

##### `200` Successful Response

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| [].id | string | 必須 | 型定義に説明なし | {} |
| [].conversation_id | string | 必須 | 型定義に説明なし | {} |
| [].question | string | 必須 | 型定義に説明なし | {} |
| [].answer | string | 必須 | 型定義に説明なし | {} |
| [].status | string | 必須 | 型定義に説明なし | {} |
| [].citations | array<Citation> | 必須 | 型定義に説明なし | {} |
| [].citations[].version_number | integer &#124; null | 任意 | 型定義に説明なし | {"anyOf": [{"type": "integer"}, {"type": "null"}]} |
| [].citations[].has_images | boolean | 任意 | 型定義に説明なし | {"default": false} |
| [].citations[].document_id | string | 必須 | 型定義に説明なし | {} |
| [].citations[].version_id | string | 必須 | 型定義に説明なし | {} |
| [].citations[].chunk_id | string | 必須 | 型定義に説明なし | {} |
| [].citations[].title | string | 必須 | 型定義に説明なし | {} |
| [].citations[].heading | string | 必須 | 型定義に説明なし | {} |
| [].citations[].manifest_hash | string | 必須 | 型定義に説明なし | {} |
| [].citations[].chunk_hash | string | 必須 | 型定義に説明なし | {} |
| [].citations[].document_revision | integer | 必須 | 型定義に説明なし | {} |
| [].model | string | 必須 | 型定義に説明なし | {} |
| [].created_at | string | 必須 | 型定義に説明なし | {"format": "date-time"} |


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

### 認証情報がない要求の拒否

認証情報なしのHTTP要求と不変項目を実テストで確認します。

```json
{
  "name": "認証情報がない要求の拒否",
  "method": "GET",
  "path": "/api/chat/00000000-0000-0000-0000-000000000001",
  "expected_status": 401,
  "expected_fields": {
    "code": "unauthenticated"
  }
}
```