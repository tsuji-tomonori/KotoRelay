<!-- 実装から生成。直接編集しない。入力SHA256: ac3b8a89c10fb6f4c0a9456ea4fb59251414105722d4188a0beaca0d8b493f26 -->

# manifestを確認して承認・却下 — インターフェース

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## Headers

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| Idempotency-Key | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "uuid", "title": "Idempotency-Key"} |


認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


## Path Parameters

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| submission_id | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "uuid", "title": "Submission Id"} |


## Query Parameters

該当する入力はありません。

## Data

媒体: `application/json`

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| manifest_hash | string | 必須 | 型定義に説明なし | {"pattern": "^[0-9a-f]{64}$"} |
| decision | string | 必須 | 型定義に説明なし | {"enum": ["approved", "rejected"]} |
| reason | string | 任意 | 型定義に説明なし | {"maxLength": 2000, "default": ""} |


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
| document_id | string | 必須 | 型定義に説明なし | {} |
| version_id | string | 必須 | 型定義に説明なし | {} |
| requested_by | string | 必須 | 型定義に説明なし | {} |
| status | string | 必須 | 型定義に説明なし | {} |
| manifest_hash | string | 必須 | 型定義に説明なし | {} |
| decided_by | string &#124; null | 必須 | 型定義に説明なし | {"anyOf": [{"type": "string"}, {"type": "null"}]} |
| reason | string | 必須 | 型定義に説明なし | {} |
| created_at | string | 必須 | 型定義に説明なし | {"format": "date-time"} |
| decided_at | string &#124; null | 必須 | 型定義に説明なし | {"anyOf": [{"type": "string", "format": "date-time"}, {"type": "null"}]} |


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
  "method": "POST",
  "path": "/api/reviews/00000000-0000-0000-0000-000000000001/decision",
  "expected_status": 401,
  "expected_fields": {
    "code": "unauthenticated"
  }
}
```