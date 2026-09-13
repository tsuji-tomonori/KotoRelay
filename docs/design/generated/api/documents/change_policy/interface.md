<!-- 実装から生成。直接編集しない。入力SHA256: 7ce322b2bb5c68dab4c51499ae55d5e49bae34d22b47e21dd6264975362b5d49 -->

# リーダーが公開範囲・公開停止・削除を管理 — インターフェース

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## Headers

該当する入力はありません。

認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


## Path Parameters

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| document_id | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "uuid", "title": "Document Id"} |


## Query Parameters

該当する入力はありません。

## Data

媒体: `application/json`

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| reason | string | 任意 | 型定義に説明なし | {"maxLength": 2000, "default": ""} |
| revision | integer | 必須 | 型定義に説明なし | {"minimum": 1.0} |
| visibility | string | 必須 | 型定義に説明なし | {"enum": ["department", "selected", "organization"]} |
| shared_departments | array<string> | 任意 | 型定義に説明なし | {"maxItems": 30} |
| status | string | 必須 | 型定義に説明なし | {"enum": ["active", "withdrawn", "deleted"]} |


## Responses

| Status | 説明 | Media type |
| --- | --- | --- |
| 200 | Successful Response | application/json |
| 422 | Validation Error | application/json |

##### `200` Successful Response

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| id | string | 必須 | 型定義に説明なし | {} |
| organization_id | string | 必須 | 型定義に説明なし | {} |
| department_id | string | 必須 | 型定義に説明なし | {} |
| title | string | 必須 | 型定義に説明なし | {} |
| created_by | string | 必須 | 型定義に説明なし | {} |
| visibility | string | 必須 | 型定義に説明なし | {} |
| shared_departments | string | 必須 | 型定義に説明なし | {} |
| status | string | 必須 | 型定義に説明なし | {} |
| revision | integer | 必須 | 型定義に説明なし | {} |
| next_version | integer | 必須 | 型定義に説明なし | {} |
| latest_version_id | string &#124; null | 必須 | 型定義に説明なし | {"anyOf": [{"type": "string"}, {"type": "null"}]} |
| updated_at | string | 必須 | 型定義に説明なし | {"format": "date-time"} |


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
  "method": "PUT",
  "path": "/api/documents/00000000-0000-0000-0000-000000000001/policy",
  "expected_status": 401,
  "expected_fields": {
    "code": "unauthenticated"
  }
}
```