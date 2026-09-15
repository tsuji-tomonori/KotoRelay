<!-- 実装から生成。直接編集しない。入力SHA256: f473ec4902a9e7cc973e702d4fbb05a99ce8c26a324da9a1f4592aab94dbd60c -->

# 文書を作成 — インターフェース

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

媒体: `application/json`

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| title | string | 必須 | 型定義に説明なし | {"maxLength": 200, "minLength": 1} |
| department_id | string | 必須 | 型定義に説明なし | {"pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"} |


## Responses

| Status | 説明 | Media type |
| --- | --- | --- |
| 201 | Successful Response | application/json |
| 422 | Validation Error | application/json |

##### `201` Successful Response

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
  "method": "POST",
  "path": "/api/documents",
  "expected_status": 401,
  "expected_fields": {
    "code": "unauthenticated"
  }
}
```