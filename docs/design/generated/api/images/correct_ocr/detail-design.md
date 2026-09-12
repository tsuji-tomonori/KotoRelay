<!-- 実装から生成。直接編集しない。入力SHA256: 31de213f242d3d7bf0d4f5957d4ef327aaacb2267a973d8e0adce1f1531ac7e1 -->

# OCRを訂正し新しいrunを保存 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: OCRを訂正し新しいrunを保存。

**Headers**

該当する入力はありません。

認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


**Path Parameters**

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| asset_id | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "uuid", "title": "Asset Id"} |


**Query Parameters**

該当する入力はありません。

**Data**

媒体: `application/json`

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| regions | array<Region> | 必須 | 型定義に説明なし | {"maxItems": 1000} |
| regions[].region_id | string &#124; null | 任意 | 型定義に説明なし | {"anyOf": [{"type": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"}, {"type": "null"}]} |
| regions[].source | string | 任意 | 型定義に説明なし | {"enum": ["detected", "human"], "default": "detected"} |
| regions[].text | string | 必須 | 型定義に説明なし | {"maxLength": 5000} |
| regions[].x | number | 必須 | 型定義に説明なし | {"maximum": 1.0, "minimum": 0.0} |
| regions[].y | number | 必須 | 型定義に説明なし | {"maximum": 1.0, "minimum": 0.0} |
| regions[].width | number | 必須 | 型定義に説明なし | {"maximum": 1.0, "minimum": 0.0} |
| regions[].height | number | 必須 | 型定義に説明なし | {"maximum": 1.0, "minimum": 0.0} |
| regions[].confidence | number &#124; null | 任意 | 型定義に説明なし | {"anyOf": [{"type": "number", "maximum": 1.0, "minimum": 0.0}, {"type": "null"}]} |
| regions[].order | integer | 必須 | 型定義に説明なし | {"minimum": 0.0} |
| confirmed | boolean | 必須 | 型定義に説明なし | {} |


## 2. 正常系前提

認証・認可と型制約を満たすこと。以下は実装の検査条件と制御分岐です。条件の成立を一律に正常系とは扱いません。

| 実装箇所 | 検査条件 | 不成立時／分岐 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:40 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:43 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:82 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/context.py:89 | allowed | not_found | 404 |
| backend/src/kotorelay/context.py:53 | q.organizations_fence(self.db, self.organization) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/images/functions.py:116 | bool(assets) | not_found | 404 |
| backend/src/kotorelay/operations/images/functions.py:120 | len(ids) == len(set(ids)) | 'invalid_region' | 422 |
| backend/src/kotorelay/operations/images/functions.py:122 | region.x + region.width <= 1.000001 and region.y + region.height <= 1.000001 | 'invalid_region' | 422 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| assets_get | assets | SELECT |
| audit_insert | audit | INSERT |
| departments_list | departments | SELECT |
| documents_get | documents | SELECT |
| memberships_list | memberships | SELECT |
| ocr_runs_insert | ocr_runs | INSERT |
| organizations_fence | organizations | UPDATE |
| organizations_get | organizations | SELECT |
| users_list | users | SELECT |

異常時はDB transactionがrollbackします。内容ハッシュ実体は孤立し得るため、公開認可には使いません。配送失敗はoutboxへ記録します。

## 4. 正常系レスポンス

| Status | 説明 | Media type |
| --- | --- | --- |
| 200 | Successful Response | application/json |
| 422 | Validation Error | application/json |

##### `200` Successful Response

型: `object`。定義: `{"type": "object", "additionalProperties": true, "title": "Response Correct Ocr"}`


##### `422` Validation Error

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| detail | array<ValidationError> | 任意 | 型定義に説明なし | {} |
| detail[].loc | array<string &#124; integer> | 必須 | 型定義に説明なし | {} |
| detail[].msg | string | 必須 | 型定義に説明なし | {} |
| detail[].type | string | 必須 | 型定義に説明なし | {} |
| detail[].input | object（追加項目はスキーマ参照） | 任意 | 型定義に説明なし | {} |
| detail[].ctx | object | 任意 | 型定義に説明なし | {} |


**応答項目の取得元**

| 実装箇所 | 返却式（DB行・変換結果・固定値） |
| --- | --- |
| backend/src/kotorelay/context.py:90 | doc |
| backend/src/kotorelay/context.py:22 | str(uuid4()) |
| backend/src/kotorelay/context.py:18 | datetime.now(UTC) |
| backend/src/kotorelay/generated/queries.py:553 | db.query('operations/images/sql/assets_get.sql', {'organization_id': organization_id, 'id': id}, AssetsRow) |
| backend/src/kotorelay/generated/queries.py:734 | db.execute('operations/system/sql/audit_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:437 | db.query('operations/groups/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/generated/queries.py:331 | db.query('operations/documents/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/generated/queries.py:473 | db.query('operations/groups/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/generated/queries.py:590 | db.execute('operations/images/sql/ocr_runs_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:487 | db.execute('operations/identity/sql/organizations_fence.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:492 | db.query('operations/identity/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/generated/queries.py:534 | db.query('operations/identity/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
| backend/src/kotorelay/operations/images/functions.py:154 | {'ocr_run': run, 'ocr': result} |
| backend/src/kotorelay/operations/images/router.py:39 | f.correct(ctx, str(asset_id), data) |
