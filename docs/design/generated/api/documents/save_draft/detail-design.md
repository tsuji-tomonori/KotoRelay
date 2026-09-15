<!-- 実装から生成。直接編集しない。入力SHA256: f473ec4902a9e7cc973e702d4fbb05a99ce8c26a324da9a1f4592aab94dbd60c -->

# 競合を検出して下書きを保存 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: 競合を検出して下書きを保存。

**Headers**

該当する入力はありません。

認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


**Path Parameters**

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| document_id | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "uuid", "title": "Document Id"} |


**Query Parameters**

該当する入力はありません。

**Data**

媒体: `application/json`

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| title | string | 必須 | 型定義に説明なし | {"maxLength": 200, "minLength": 1} |
| body | string | 必須 | 型定義に説明なし | {"maxLength": 100000} |
| revision | integer | 必須 | 型定義に説明なし | {"minimum": 1.0} |
| placements | array<Placement> | 任意 | 型定義に説明なし | {"maxItems": 10} |
| placements[].id | string | 必須 | 型定義に説明なし | {"pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"} |
| placements[].asset_id | string | 必須 | 型定義に説明なし | {"pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"} |
| placements[].ocr_run_id | string | 必須 | 型定義に説明なし | {"pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"} |
| placements[].offset | integer | 必須 | 型定義に説明なし | {"maximum": 100000.0, "minimum": 0.0} |
| placements[].heading | string | 任意 | 型定義に説明なし | {"maxLength": 200, "default": ""} |
| placements[].alt_text | string | 任意 | 型定義に説明なし | {"maxLength": 1000, "default": ""} |
| placements[].caption | string | 任意 | 型定義に説明なし | {"maxLength": 2000, "default": ""} |


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
| backend/src/kotorelay/operations/documents/save_draft/functions.py:50 | row.revision == data.revision | 'conflict' | 409 |
| backend/src/kotorelay/operations/documents/save_draft/functions.py:19 | len({p.id for p in data.placements}) == len(data.placements) | 'invalid_placement' | 422 |
| backend/src/kotorelay/operations/documents/save_draft/functions.py:27 | bool(assets) and bool(runs) | 'invalid_placement' | 422 |
| backend/src/kotorelay/operations/documents/save_draft/functions.py:28 | assets[0].document_id == doc.id and runs[0].asset_id == assets[0].id and (runs[0].document_id == doc.id) and (placement.offset <= len(data.body)) | 'invalid_placement' | 422 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| kotorelay.operations.documents.save_draft.generated.queries.assets_get | assets | SELECT |
| kotorelay.operations.documents.save_draft.generated.queries.documents_update | documents | UPDATE |
| kotorelay.operations.documents.save_draft.generated.queries.drafts_list | drafts | SELECT |
| kotorelay.operations.documents.save_draft.generated.queries.drafts_update | drafts | UPDATE |
| kotorelay.operations.documents.save_draft.generated.queries.ocr_runs_get | ocr_runs | SELECT |
| kotorelay.operations.documents.shared.generated.queries.drafts_list | drafts | SELECT |
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

型: `object`。定義: `{"type": "object", "additionalProperties": true, "title": "Response Save Draft"}`


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
| backend/src/kotorelay/context.py:20 | datetime.now(UTC) |
| backend/src/kotorelay/operations/documents/save_draft/functions.py:96 | ctx.fence() |
| backend/src/kotorelay/operations/documents/save_draft/functions.py:40 | ctx.document(str(document_id), 'author') |
| backend/src/kotorelay/operations/documents/save_draft/functions.py:83 | q.documents_update(ctx.db, q.DocumentsUpdateParams.model_validate(doc.model_copy(update={'title': data.title, 'revision': doc.revision + 1, 'updated_at': now()}), from_attributes=True)) |
| backend/src/kotorelay/operations/documents/save_draft/functions.py:45 | q.drafts_list(ctx.db, q.DraftsListParams(organization_id=ctx.org)) |
| backend/src/kotorelay/operations/documents/save_draft/functions.py:62 | q.drafts_update(ctx.db, q.DraftsUpdateParams.model_validate(row.model_copy(update={'body_key': key, 'body_hash': key, 'revision': row.revision + 1, 'updated_by': ctx.user.id, 'placements': json.dumps([p.model_dump() for p in data.placements])}), from_attributes=True)) |
| backend/src/kotorelay/operations/documents/save_draft/functions.py:101 | row.document_id == document_id |
| backend/src/kotorelay/operations/documents/save_draft/functions.py:55 | ctx.objects.put(data.body.encode(), 'text/markdown') |
| backend/src/kotorelay/operations/documents/save_draft/functions.py:50 | require(row.revision == data.revision, 'conflict', 409) |
| backend/src/kotorelay/operations/documents/save_draft/generated/queries.py:43 | db.query('operations/documents/save_draft/sql/001_assets_get.sql', params.model_dump(), AssetsGetRow) |
| backend/src/kotorelay/operations/documents/save_draft/generated/queries.py:68 | db.execute('operations/documents/save_draft/sql/002_documents_update.sql', params.model_dump()) |
| backend/src/kotorelay/operations/documents/save_draft/generated/queries.py:96 | db.query('operations/documents/save_draft/sql/003_drafts_list.sql', params.model_dump(), DraftsListRow) |
| backend/src/kotorelay/operations/documents/save_draft/generated/queries.py:119 | db.execute('operations/documents/save_draft/sql/004_drafts_update.sql', params.model_dump()) |
| backend/src/kotorelay/operations/documents/save_draft/generated/queries.py:150 | db.query('operations/documents/save_draft/sql/005_ocr_runs_get.sql', params.model_dump(), OcrRunsGetRow) |
| backend/src/kotorelay/operations/documents/save_draft/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/documents/save_draft/router.py:38 | build_response(draft_functions.build_draft_data(current_document, current_draft, body)) |
| backend/src/kotorelay/operations/documents/shared/functions.py:12 | ctx.document(document_id, 'draft') |
| backend/src/kotorelay/operations/documents/shared/functions.py:33 | {'document': doc, 'body': body, 'revision': row.revision, 'placements': json.loads(row.placements)} |
| backend/src/kotorelay/operations/documents/shared/functions.py:26 | ctx.objects.get(row.body_key, row.body_hash).decode() |
| backend/src/kotorelay/operations/documents/shared/functions.py:17 | next((row for row in q.drafts_list(ctx.db, q.DraftsListParams(organization_id=ctx.org)) if row.document_id == document_id)) |
| backend/src/kotorelay/operations/documents/shared/generated/queries.py:36 | db.query('operations/documents/shared/sql/001_drafts_list.sql', params.model_dump(), DraftsListRow) |
| backend/src/kotorelay/operations/system/authorization/functions.py:6 | operation == 'read' |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:63 | db.query('operations/system/authorization/sql/002_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:98 | db.query('operations/system/authorization/sql/003_documents_get.sql', params.model_dump(), DocumentsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:176 | db.query('operations/system/authorization/sql/006_memberships_list.sql', params.model_dump(), MembershipsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:194 | db.execute('operations/system/authorization/sql/007_organizations_fence.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:220 | db.query('operations/system/authorization/sql/008_organizations_get.sql', params.model_dump(), OrganizationsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:248 | db.query('operations/system/authorization/sql/009_users_list.sql', params.model_dump(), UsersListRow) |
