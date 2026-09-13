<!-- 実装から生成。直接編集しない。入力SHA256: 987c18a693c5fa5c9f59f732c65771f1c047c0829e22a5d72b689276aae93c56 -->

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
| backend/src/kotorelay/context.py:41 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:44 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:71 | doc.status != 'active' or not self.memberships | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:73 | doc.visibility == 'organization' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:75 | self.member(doc.department_id) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:61 | m.department_id == department_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:20 | department_id and scope in {'manage', 'work'} | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:31 | scope == 'manage' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:33 | scope == 'work' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:21 | ctx.permission(department_id, 'manage' if scope == 'manage' else 'draft') | 'forbidden' | 403 |
| backend/src/kotorelay/operations/documents/list_documents/router.py:35 | page | then / else の実装分岐 | 制御フロー参照 |


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
| backend/src/kotorelay/context.py:77 | doc.visibility == 'selected' and any((self.member(department) for department in json.loads(doc.shared_departments))) |
| backend/src/kotorelay/context.py:72 | False |
| backend/src/kotorelay/context.py:74 | True |
| backend/src/kotorelay/context.py:76 | True |
| backend/src/kotorelay/context.py:68 | False |
| backend/src/kotorelay/context.py:62 | {'author': m.can_author, 'review': m.can_review, 'manage': m.leader, 'draft': m.can_author or m.can_review}.get(operation, False) |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:90 | {'items': items, 'has_next': len(docs) > limit} |
| backend/src/kotorelay/operations/documents/list_documents/functions.py:50 | sorted(docs, key=lambda d: d.updated_at, reverse=True)[offset:offset + limit] |
| backend/src/kotorelay/operations/documents/list_documents/generated/queries.py:16 | db.query('operations/documents/list_documents/sql/chunks_list.sql', {'organization_id': organization_id}, ChunksRow) |
| backend/src/kotorelay/operations/documents/list_documents/generated/queries.py:27 | db.query('operations/documents/list_documents/sql/documents_by_department.sql', {'organization_id': organization_id, 'department_id': department_id}, DocumentsRow) |
| backend/src/kotorelay/operations/documents/list_documents/generated/queries.py:36 | db.query('operations/documents/list_documents/sql/documents_list.sql', {'organization_id': organization_id}, DocumentsRow) |
| backend/src/kotorelay/operations/documents/list_documents/generated/queries.py:45 | db.query('operations/documents/list_documents/sql/submissions_list.sql', {'organization_id': organization_id}, SubmissionsRow) |
| backend/src/kotorelay/operations/documents/list_documents/generated/queries.py:54 | db.query('operations/documents/list_documents/sql/versions_list.sql', {'organization_id': organization_id}, VersionsRow) |
| backend/src/kotorelay/operations/documents/list_documents/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/documents/list_documents/router.py:39 | build_response(f.list_documents(ctx, scope, offset, limit, search, department, status)) |
| backend/src/kotorelay/operations/documents/list_documents/router.py:36 | build_response(f.document_page(ctx, scope, offset, limit, search, department, status)) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:25 | db.query('operations/system/authorization/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:59 | db.query('operations/system/authorization/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:75 | db.query('operations/system/authorization/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:84 | db.query('operations/system/authorization/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
