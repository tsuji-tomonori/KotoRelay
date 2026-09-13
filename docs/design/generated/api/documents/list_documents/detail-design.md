<!-- 実装から生成。直接編集しない。入力SHA256: 7ce322b2bb5c68dab4c51499ae55d5e49bae34d22b47e21dd6264975362b5d49 -->

# 閲覧可能な文書を検索 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: 閲覧可能な文書を検索。

**Headers**

該当する入力はありません。

認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


**Path Parameters**

該当する入力はありません。

**Query Parameters**

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| scope | string | 任意 | OpenAPIの型制約に従う | {"enum": ["read", "work", "manage"], "type": "string", "default": "read", "title": "Scope"} |
| offset | integer | 任意 | OpenAPIの型制約に従う | {"type": "integer", "minimum": 0, "default": 0, "title": "Offset"} |
| limit | integer | 任意 | OpenAPIの型制約に従う | {"type": "integer", "maximum": 100, "minimum": 1, "default": 30, "title": "Limit"} |
| search | string | 任意 | OpenAPIの型制約に従う | {"type": "string", "maxLength": 200, "default": "", "title": "Search"} |
| department_id | string &#124; null | 任意 | OpenAPIの型制約に従う | {"anyOf": [{"type": "string", "format": "uuid"}, {"type": "null"}], "title": "Department Id"} |
| status | string | 任意 | OpenAPIの型制約に従う | {"enum": ["", "active", "withdrawn", "deleted"], "type": "string", "default": "", "title": "Status"} |
| page | boolean | 任意 | OpenAPIの型制約に従う | {"type": "boolean", "default": false, "title": "Page"} |


**Data**

リクエスト本文はありません。

## 2. 正常系前提

認証・認可と型制約を満たすこと。以下は実装の検査条件と制御分岐です。条件の成立を一律に正常系とは扱いません。

| 実装箇所 | 検査条件 | 不成立時／分岐 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:43 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:50 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:89 | doc.status != 'active' or not self.memberships | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:91 | doc.visibility == 'organization' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:93 | self.member(doc.department_id) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:79 | m.department_id == department_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:22 | ctx.permission(department_id, 'manage' if scope == 'manage' else 'draft') | 'forbidden' | 403 |
| backend/src/kotorelay/operations/documents/list_documents/router.py:52 | department_id and f.requires_department_permission(department_id, scope) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/documents/list_documents/router.py:57 | f.is_management_scope(scope) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/documents/list_documents/router.py:59 | f.is_authoring_scope(scope) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/documents/list_documents/router.py:38 | page | then / else の実装分岐 | 制御フロー参照 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| kotorelay.operations.documents.list_documents.generated.queries.chunks_list | chunks | SELECT |
| kotorelay.operations.documents.list_documents.generated.queries.documents_by_department | documents | SELECT |
| kotorelay.operations.documents.list_documents.generated.queries.documents_list | documents | SELECT |
| kotorelay.operations.documents.list_documents.generated.queries.submissions_list | submissions | SELECT |
| kotorelay.operations.documents.list_documents.generated.queries.versions_list | versions | SELECT |
| kotorelay.operations.system.authorization.generated.queries.departments_list | departments | SELECT |
| kotorelay.operations.system.authorization.generated.queries.memberships_list | memberships | SELECT |
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


**応答項目の取得元**

| 実装箇所 | 返却式（DB行・変換結果・固定値） |
| --- | --- |
| backend/src/kotorelay/context.py:95 | doc.visibility == 'selected' and any((self.member(department) for department in json.loads(doc.shared_departments))) |
| backend/src/kotorelay/context.py:90 | False |
| backend/src/kotorelay/context.py:92 | True |
| backend/src/kotorelay/context.py:94 | True |
| backend/src/kotorelay/context.py:86 | False |
| backend/src/kotorelay/context.py:80 | {'author': m.can_author, 'review': m.can_review, 'manage': m.leader, 'draft': m.can_author or m.can_review}.get(operation, False) |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:167 | item |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:131 | {'published_number': version.number if version else None, 'approved_at': approval.decided_at if approval else None, 'index_ready': bool(version and any((c.version_id == version.id and c.ready for c in chunks))), 'summary': ctx.objects.get(version.body_key, version.body_hash).decode()[:180] if version and scope == 'read' else '', 'review_status': latest.status if latest and scope != 'read' else None, 'review_number': versions[latest.version_id].number if latest and scope != 'read' else None} |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:149 | {'items': items, 'has_next': len(docs) > limit} |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:111 | q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org)) |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:31 | q.documents_by_department(ctx.db, q.DocumentsByDepartmentParams(organization_id=ctx.org, department_id=department_id)) |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:38 | q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org)) |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:55 | bool(scope == 'work') |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:43 | bool(scope == 'manage') |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:74 | {v.id: v for v in q.versions_list(ctx.db, q.VersionsListParams(organization_id=ctx.org))} |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:101 | {v.id: v for v in q.versions_list(ctx.db, q.VersionsListParams(organization_id=ctx.org))} |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:22 | require(ctx.permission(department_id, 'manage' if scope == 'manage' else 'draft'), 'forbidden', 403) |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:15 | bool(department_id and scope in {'manage', 'work'}) |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:50 | [d for d in docs if ctx.permission(d.department_id, 'manage')] |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:62 | [d for d in docs if d.status != 'deleted' and ctx.permission(d.department_id, 'draft')] |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:69 | [d for d in docs if d.latest_version_id and ctx.can_read(d)] |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:81 | [d.model_copy(update={'title': versions[d.latest_version_id].title}) for d in docs if d.latest_version_id in versions] |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:92 | [d for d in docs if search.casefold() in d.title.casefold() and (not status or d.status == status)] |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:118 | [s for s in submissions if s.document_id == doc.id] |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:106 | q.submissions_list(ctx.db, q.SubmissionsListParams(organization_id=ctx.org)) |
| backend/src/kotorelay/operations/documents/list_documents/generated/queries.py:43 | db.query('operations/documents/list_documents/sql/001_chunks_list.sql', params.model_dump(), ChunksListRow) |
| backend/src/kotorelay/operations/documents/list_documents/generated/queries.py:80 | db.query('operations/documents/list_documents/sql/002_documents_by_department.sql', params.model_dump(), DocumentsByDepartmentRow) |
| backend/src/kotorelay/operations/documents/list_documents/generated/queries.py:114 | db.query('operations/documents/list_documents/sql/003_documents_list.sql', params.model_dump(), DocumentsListRow) |
| backend/src/kotorelay/operations/documents/list_documents/generated/queries.py:147 | db.query('operations/documents/list_documents/sql/004_submissions_list.sql', params.model_dump(), SubmissionsListRow) |
| backend/src/kotorelay/operations/documents/list_documents/generated/queries.py:180 | db.query('operations/documents/list_documents/sql/005_versions_list.sql', params.model_dump(), VersionsListRow) |
| backend/src/kotorelay/operations/documents/list_documents/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/documents/list_documents/router.py:66 | sorted(docs, key=lambda d: d.updated_at, reverse=True)[offset:offset + limit] |
| backend/src/kotorelay/operations/documents/list_documents/router.py:85 | f.build_document_page_2(items, limit, docs) |
| backend/src/kotorelay/operations/documents/list_documents/router.py:40 | build_response(_select_documents(ctx, scope, offset, limit, search, department, status)) |
| backend/src/kotorelay/operations/documents/list_documents/router.py:39 | build_response(document_page(ctx, scope, offset, limit, search, department, status)) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:63 | db.query('operations/system/authorization/sql/002_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:176 | db.query('operations/system/authorization/sql/006_memberships_list.sql', params.model_dump(), MembershipsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:220 | db.query('operations/system/authorization/sql/008_organizations_get.sql', params.model_dump(), OrganizationsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:248 | db.query('operations/system/authorization/sql/009_users_list.sql', params.model_dump(), UsersListRow) |
