<!-- 実装から生成。直接編集しない。入力SHA256: f473ec4902a9e7cc973e702d4fbb05a99ce8c26a324da9a1f4592aab94dbd60c -->

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
| backend/src/kotorelay/context.py:45 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:52 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:110 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/context.py:117 | allowed | not_found | 404 |
| backend/src/kotorelay/context.py:67 | q.organizations_fence(self.db, q.OrganizationsFenceParams.model_validate(self.organization, from_attributes=True)) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/images/correct_ocr/functions.py:23 | bool(assets) | not_found | 404 |
| backend/src/kotorelay/operations/images/correct_ocr/functions.py:43 | region.x + region.width <= 1.000001 and region.y + region.height <= 1.000001 | 'invalid_region' | 422 |
| backend/src/kotorelay/operations/images/correct_ocr/functions.py:38 | len(ids) == len(set(ids)) | 'invalid_region' | 422 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| kotorelay.operations.images.correct_ocr.generated.queries.assets_get | assets | SELECT |
| kotorelay.operations.images.correct_ocr.generated.queries.ocr_runs_insert | ocr_runs | INSERT |
| kotorelay.operations.system.authorization.generated.queries.audit_insert | audit | INSERT |
| kotorelay.operations.system.authorization.generated.queries.departments_list | departments | SELECT |
| kotorelay.operations.system.authorization.generated.queries.documents_get | documents | SELECT |
| kotorelay.operations.system.authorization.generated.queries.memberships_list | memberships | SELECT |
| kotorelay.operations.system.authorization.generated.queries.organizations_fence | organizations | UPDATE |
| kotorelay.operations.system.authorization.generated.queries.organizations_get | organizations | SELECT |
| kotorelay.operations.system.authorization.generated.queries.users_list | users | SELECT |

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
| backend/src/kotorelay/context.py:118 | doc |
| backend/src/kotorelay/context.py:24 | str(uuid4()) |
| backend/src/kotorelay/context.py:20 | datetime.now(UTC) |
| backend/src/kotorelay/operations/images/correct_ocr/functions.py:18 | q.assets_get(ctx.db, q.AssetsGetParams(organization_id=ctx.org, id=str(asset_id))) |
| backend/src/kotorelay/operations/images/correct_ocr/functions.py:108 | {'ocr_run': run, 'ocr': result} |
| backend/src/kotorelay/operations/images/correct_ocr/functions.py:73 | models.OcrRunsRow(id=new_id(), organization_id=ctx.org, document_id=asset.document_id, asset_id=asset.id, result_key=key, result_hash=key, engine=result.engine, status='ready', confirmed=data.confirmed, created_at=now()) |
| backend/src/kotorelay/operations/images/correct_ocr/functions.py:101 | ctx.fence() |
| backend/src/kotorelay/operations/images/correct_ocr/functions.py:89 | q.ocr_runs_insert(ctx.db, q.OcrRunsInsertParams.model_validate(run, from_attributes=True)) |
| backend/src/kotorelay/operations/images/correct_ocr/functions.py:62 | ctx.objects.put(result.model_dump_json().encode(), 'application/json') |
| backend/src/kotorelay/operations/images/correct_ocr/functions.py:96 | ctx.audit('ocr_correction', asset.document_id) |
| backend/src/kotorelay/operations/images/correct_ocr/functions.py:23 | require(bool(assets)) |
| backend/src/kotorelay/operations/images/correct_ocr/functions.py:33 | [r.region_id for r in data.regions if r.region_id is not None] |
| backend/src/kotorelay/operations/images/correct_ocr/functions.py:52 | [r.model_copy(update={'region_id': r.region_id or new_id(), 'source': 'human', 'confidence': None}) for r in data.regions] |
| backend/src/kotorelay/operations/images/correct_ocr/functions.py:43 | require(region.x + region.width <= 1.000001 and region.y + region.height <= 1.000001, 'invalid_region', 422) |
| backend/src/kotorelay/operations/images/correct_ocr/functions.py:38 | require(len(ids) == len(set(ids)), 'invalid_region', 422) |
| backend/src/kotorelay/operations/images/correct_ocr/generated/queries.py:41 | db.query('operations/images/correct_ocr/sql/001_assets_get.sql', params.model_dump(), AssetsGetRow) |
| backend/src/kotorelay/operations/images/correct_ocr/generated/queries.py:64 | db.execute('operations/images/correct_ocr/sql/002_ocr_runs_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/images/correct_ocr/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/images/correct_ocr/router.py:46 | build_response(f.build_correct_ocr(run, result)) |
| backend/src/kotorelay/operations/system/authorization/functions.py:6 | operation == 'read' |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:39 | db.execute('operations/system/authorization/sql/001_audit_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:63 | db.query('operations/system/authorization/sql/002_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:98 | db.query('operations/system/authorization/sql/003_documents_get.sql', params.model_dump(), DocumentsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:176 | db.query('operations/system/authorization/sql/006_memberships_list.sql', params.model_dump(), MembershipsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:194 | db.execute('operations/system/authorization/sql/007_organizations_fence.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:220 | db.query('operations/system/authorization/sql/008_organizations_get.sql', params.model_dump(), OrganizationsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:248 | db.query('operations/system/authorization/sql/009_users_list.sql', params.model_dump(), UsersListRow) |
