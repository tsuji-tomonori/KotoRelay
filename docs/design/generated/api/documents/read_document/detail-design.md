<!-- 実装から生成。直接編集しない。入力SHA256: dc958b6e6841a9f29856eb932e8271e37a6d4416a3266624301c411c89949f81 -->

# 承認版または担当版を表示 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: 承認版または担当版を表示。

**Headers**

該当する入力はありません。

認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


**Path Parameters**

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| document_id | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "uuid", "title": "Document Id"} |


**Query Parameters**

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| version_id | string &#124; null | 任意 | OpenAPIの型制約に従う | {"anyOf": [{"type": "string", "format": "uuid"}, {"type": "null"}], "title": "Version Id"} |


**Data**

リクエスト本文はありません。

## 2. 正常系前提

認証・認可と型制約を満たすこと。以下は実装の検査条件と制御分岐です。条件の成立を一律に正常系とは扱いません。

| 実装箇所 | 検査条件 | 不成立時／分岐 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:45 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:52 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:95 | doc.status != 'active' or not self.memberships | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:97 | doc.visibility == 'organization' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:99 | self.member(doc.department_id) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:84 | m.department_id == department_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:125 | not self.permission(doc.department_id, 'draft') | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:123 | bool(rows) and rows[0].document_id == doc.id | not_found | 404 |
| backend/src/kotorelay/context.py:127 | digest(version.manifest.encode()) == version.manifest_hash | 'integrity' | 503 |
| backend/src/kotorelay/context.py:126 | self.can_read(doc) and doc.latest_version_id == version.id | not_found | 404 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/documents/read_document/functions.py:22 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/operations/documents/read_document/functions.py:32 | ctx.can_read(doc) or ctx.permission(doc.department_id, 'draft') | not_found | 404 |
| backend/src/kotorelay/operations/documents/read_document/functions.py:27 | doc.status != 'deleted' | not_found | 404 |
| backend/src/kotorelay/operations/documents/read_document/functions.py:37 | chosen is not None | not_found | 404 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| kotorelay.operations.documents.read_document.generated.queries.chunks_list | chunks | SELECT |
| kotorelay.operations.documents.read_document.generated.queries.documents_get | documents | SELECT |
| kotorelay.operations.system.authorization.generated.queries.departments_list | departments | SELECT |
| kotorelay.operations.system.authorization.generated.queries.memberships_list | memberships | SELECT |
| kotorelay.operations.system.authorization.generated.queries.organizations_get | organizations | SELECT |
| kotorelay.operations.system.authorization.generated.queries.users_list | users | SELECT |
| kotorelay.operations.system.authorization.generated.queries.versions_get | versions | SELECT |

異常時はDB transactionがrollbackします。内容ハッシュ実体は孤立し得るため、公開認可には使いません。配送失敗はoutboxへ記録します。

## 4. 正常系レスポンス

| Status | 説明 | Media type |
| --- | --- | --- |
| 200 | Successful Response | application/json |
| 422 | Validation Error | application/json |

##### `200` Successful Response

型: `object`。定義: `{"type": "object", "additionalProperties": true, "title": "Response Read Document"}`


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
| backend/src/kotorelay/context.py:101 | doc.visibility == 'selected' and any((self.member(department) for department in json.loads(doc.shared_departments))) |
| backend/src/kotorelay/context.py:96 | False |
| backend/src/kotorelay/context.py:98 | True |
| backend/src/kotorelay/context.py:100 | True |
| backend/src/kotorelay/context.py:91 | False |
| backend/src/kotorelay/context.py:85 | {'author': m.can_author, 'review': m.can_review, 'manage': m.leader, 'draft': m.can_author or m.can_review}.get(operation, False) |
| backend/src/kotorelay/context.py:129 | version |
| backend/src/kotorelay/objects.py:17 | hashlib.sha256(data).hexdigest() |
| backend/src/kotorelay/operations/documents/read_document/functions.py:51 | {'document': doc.model_copy(update={'title': version.title}), 'version': version, 'body': ctx.objects.get(version.body_key, version.body_hash).decode(), 'index_ready': any((c.version_id == version.id and c.ready for c in q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org))))} |
| backend/src/kotorelay/operations/documents/read_document/functions.py:15 | q.documents_get(ctx.db, q.DocumentsGetParams(organization_id=ctx.org, id=str(document_id))) |
| backend/src/kotorelay/operations/documents/read_document/functions.py:64 | bool(version_id) |
| backend/src/kotorelay/operations/documents/read_document/functions.py:22 | require(bool(rows)) |
| backend/src/kotorelay/operations/documents/read_document/functions.py:32 | require(ctx.can_read(doc) or ctx.permission(doc.department_id, 'draft')) |
| backend/src/kotorelay/operations/documents/read_document/functions.py:27 | require(doc.status != 'deleted') |
| backend/src/kotorelay/operations/documents/read_document/functions.py:37 | require(chosen is not None) |
| backend/src/kotorelay/operations/documents/read_document/functions.py:44 | ctx.version(doc, str(chosen)) |
| backend/src/kotorelay/operations/documents/read_document/generated/queries.py:41 | db.query('operations/documents/read_document/sql/001_chunks_list.sql', params.model_dump(), ChunksListRow) |
| backend/src/kotorelay/operations/documents/read_document/generated/queries.py:76 | db.query('operations/documents/read_document/sql/002_documents_get.sql', params.model_dump(), DocumentsGetRow) |
| backend/src/kotorelay/operations/documents/read_document/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/documents/read_document/router.py:35 | build_response(f.build_read_document(version, doc, ctx)) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:63 | db.query('operations/system/authorization/sql/002_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:176 | db.query('operations/system/authorization/sql/006_memberships_list.sql', params.model_dump(), MembershipsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:220 | db.query('operations/system/authorization/sql/008_organizations_get.sql', params.model_dump(), OrganizationsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:248 | db.query('operations/system/authorization/sql/009_users_list.sql', params.model_dump(), UsersListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:280 | db.query('operations/system/authorization/sql/010_versions_get.sql', params.model_dump(), VersionsGetRow) |
