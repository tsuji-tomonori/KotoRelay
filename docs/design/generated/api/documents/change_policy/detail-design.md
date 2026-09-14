<!-- 実装から生成。直接編集しない。入力SHA256: ac3b8a89c10fb6f4c0a9456ea4fb59251414105722d4188a0beaca0d8b493f26 -->

# リーダーが公開範囲・公開停止・削除を管理 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: リーダーが公開範囲・公開停止・削除を管理。

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
| reason | string | 任意 | 型定義に説明なし | {"maxLength": 2000, "default": ""} |
| revision | integer | 必須 | 型定義に説明なし | {"minimum": 1.0} |
| visibility | string | 必須 | 型定義に説明なし | {"enum": ["department", "selected", "organization"]} |
| shared_departments | array<string> | 任意 | 型定義に説明なし | {"maxItems": 30} |
| status | string | 必須 | 型定義に説明なし | {"enum": ["active", "withdrawn", "deleted"]} |


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
| backend/src/kotorelay/operations/documents/change_policy/functions.py:30 | data.status != 'deleted' or bool(data.reason.strip()) | 'reason_required' | 422 |
| backend/src/kotorelay/operations/documents/change_policy/functions.py:25 | doc.revision == data.revision | 'conflict' | 409 |
| backend/src/kotorelay/operations/documents/change_policy/functions.py:44 | set(data.shared_departments) <= departments | 'forbidden' | 422 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| kotorelay.operations.documents.change_policy.generated.queries.departments_list | departments | SELECT |
| kotorelay.operations.documents.change_policy.generated.queries.documents_update | documents | UPDATE |
| kotorelay.operations.documents.change_policy.generated.queries.outbox_insert | outbox | INSERT |
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


**応答項目の取得元**

| 実装箇所 | 返却式（DB行・変換結果・固定値） |
| --- | --- |
| backend/src/kotorelay/context.py:118 | doc |
| backend/src/kotorelay/context.py:24 | str(uuid4()) |
| backend/src/kotorelay/context.py:20 | datetime.now(UTC) |
| backend/src/kotorelay/operations/documents/change_policy/functions.py:51 | doc.model_copy(update={'visibility': data.visibility, 'shared_departments': json.dumps(data.shared_departments), 'status': data.status, 'revision': doc.revision + 1, 'updated_at': now()}) |
| backend/src/kotorelay/operations/documents/change_policy/functions.py:98 | ctx.fence() |
| backend/src/kotorelay/operations/documents/change_policy/functions.py:35 | {d.id for d in q.departments_list(ctx.db, q.DepartmentsListParams(organization_id=ctx.org)) if d.active} |
| backend/src/kotorelay/operations/documents/change_policy/functions.py:18 | ctx.document(str(document_id), 'manage') |
| backend/src/kotorelay/operations/documents/change_policy/functions.py:64 | q.documents_update(ctx.db, q.DocumentsUpdateParams.model_validate(updated, from_attributes=True)) |
| backend/src/kotorelay/operations/documents/change_policy/functions.py:73 | q.outbox_insert(ctx.db, q.OutboxInsertParams(id=new_id(), organization_id=ctx.org, document_id=doc.id, version_id=doc.latest_version_id, kind='purge' if data.status == 'deleted' else 'index', status='pending', attempts=0, error_code='', created_at=now())) |
| backend/src/kotorelay/operations/documents/change_policy/functions.py:93 | ctx.audit('policy', doc.id, before=doc.status, after=data.status, reason=data.reason) |
| backend/src/kotorelay/operations/documents/change_policy/functions.py:30 | require(data.status != 'deleted' or bool(data.reason.strip()), 'reason_required', 422) |
| backend/src/kotorelay/operations/documents/change_policy/functions.py:25 | require(doc.revision == data.revision, 'conflict', 409) |
| backend/src/kotorelay/operations/documents/change_policy/functions.py:44 | require(set(data.shared_departments) <= departments, 'forbidden', 422) |
| backend/src/kotorelay/operations/documents/change_policy/generated/queries.py:34 | db.query('operations/documents/change_policy/sql/001_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/documents/change_policy/generated/queries.py:61 | db.execute('operations/documents/change_policy/sql/002_documents_update.sql', params.model_dump()) |
| backend/src/kotorelay/operations/documents/change_policy/generated/queries.py:83 | db.execute('operations/documents/change_policy/sql/003_outbox_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/documents/change_policy/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/documents/change_policy/router.py:37 | build_response(updated) |
| backend/src/kotorelay/operations/system/authorization/functions.py:6 | operation == 'read' |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:39 | db.execute('operations/system/authorization/sql/001_audit_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:63 | db.query('operations/system/authorization/sql/002_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:98 | db.query('operations/system/authorization/sql/003_documents_get.sql', params.model_dump(), DocumentsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:176 | db.query('operations/system/authorization/sql/006_memberships_list.sql', params.model_dump(), MembershipsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:194 | db.execute('operations/system/authorization/sql/007_organizations_fence.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:220 | db.query('operations/system/authorization/sql/008_organizations_get.sql', params.model_dump(), OrganizationsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:248 | db.query('operations/system/authorization/sql/009_users_list.sql', params.model_dump(), UsersListRow) |
