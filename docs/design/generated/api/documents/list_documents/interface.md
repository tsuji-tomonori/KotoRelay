<!-- 実装から生成。直接編集しない。入力SHA256: a4642be092686b22c6cb0bbcfdd011c0a0c93352fc1191e08d5c7dfccac4e973 -->

# 閲覧可能な文書を検索 — インターフェース

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
| scope | string | 任意 | OpenAPIの型制約に従う | {"enum": ["read", "work", "manage"], "type": "string", "default": "read", "title": "Scope"} |
| offset | integer | 任意 | OpenAPIの型制約に従う | {"type": "integer", "minimum": 0, "default": 0, "title": "Offset"} |
| limit | integer | 任意 | OpenAPIの型制約に従う | {"type": "integer", "maximum": 100, "minimum": 1, "default": 30, "title": "Limit"} |
| search | string | 任意 | OpenAPIの型制約に従う | {"type": "string", "maxLength": 200, "default": "", "title": "Search"} |
| department_id | string &#124; null | 任意 | OpenAPIの型制約に従う | {"anyOf": [{"type": "string", "format": "uuid"}, {"type": "null"}], "title": "Department Id"} |
| status | string | 任意 | OpenAPIの型制約に従う | {"enum": ["", "active", "withdrawn", "deleted"], "type": "string", "default": "", "title": "Status"} |
| page | boolean | 任意 | OpenAPIの型制約に従う | {"type": "boolean", "default": false, "title": "Page"} |


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
| <anyOf:1>[].id | string | 必須 | 型定義に説明なし | {} |
| <anyOf:1>[].organization_id | string | 必須 | 型定義に説明なし | {} |
| <anyOf:1>[].department_id | string | 必須 | 型定義に説明なし | {} |
| <anyOf:1>[].title | string | 必須 | 型定義に説明なし | {} |
| <anyOf:1>[].created_by | string | 必須 | 型定義に説明なし | {} |
| <anyOf:1>[].visibility | string | 必須 | 型定義に説明なし | {} |
| <anyOf:1>[].shared_departments | string | 必須 | 型定義に説明なし | {} |
| <anyOf:1>[].status | string | 必須 | 型定義に説明なし | {} |
| <anyOf:1>[].revision | integer | 必須 | 型定義に説明なし | {} |
| <anyOf:1>[].next_version | integer | 必須 | 型定義に説明なし | {} |
| <anyOf:1>[].latest_version_id | string &#124; null | 必須 | 型定義に説明なし | {"anyOf": [{"type": "string"}, {"type": "null"}]} |
| <anyOf:1>[].updated_at | string | 必須 | 型定義に説明なし | {"format": "date-time"} |


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
  "path": "/api/documents",
  "expected_status": 401,
  "expected_fields": {
    "code": "unauthenticated"
  }
}
```