<!-- 実装から生成。直接編集しない。入力SHA256: a4642be092686b22c6cb0bbcfdd011c0a0c93352fc1191e08d5c7dfccac4e973 -->

# 実閲覧を一意IDで記録 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: 実閲覧を一意IDで記録。

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
| id | string | 必須 | 型定義に説明なし | {"pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"} |
| department_id | string | 必須 | 型定義に説明なし | {"pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"} |


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
| backend/src/kotorelay/operations/metrics/record_view/functions.py:29 | ctx.member(data.department_id) | 'forbidden' | 403 |
| backend/src/kotorelay/operations/metrics/record_view/functions.py:22 | bool(doc.latest_version_id) | not_found | 404 |
| backend/src/kotorelay/operations/metrics/record_view/functions.py:41 | previous[0].document_id == doc.id and previous[0].department_id == data.department_id and (previous[0].kind == 'view') | 'idempotency_conflict' | 409 |
| backend/src/kotorelay/operations/metrics/record_view/router.py:32 | f.has_previous_view(previous) | then / else の実装分岐 | 制御フロー参照 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| kotorelay.operations.metrics.record_view.generated.queries.events_get | events | SELECT |
| kotorelay.operations.metrics.record_view.generated.queries.events_insert | events | INSERT |
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

型: `object`。定義: `{"type": "object", "additionalProperties": {"type": "boolean"}, "title": "Response Record View"}`


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
| backend/src/kotorelay/context.py:79 | any((m.department_id == department_id for m in self.memberships)) |
| backend/src/kotorelay/context.py:20 | datetime.now(UTC) |
| backend/src/kotorelay/context.py:28 | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| backend/src/kotorelay/operations/metrics/record_view/functions.py:52 | {'recorded': False} |
| backend/src/kotorelay/operations/metrics/record_view/functions.py:85 | {'recorded': True} |
| backend/src/kotorelay/operations/metrics/record_view/functions.py:80 | ctx.fence() |
| backend/src/kotorelay/operations/metrics/record_view/functions.py:17 | ctx.document(str(document_id)) |
| backend/src/kotorelay/operations/metrics/record_view/functions.py:34 | q.events_get(ctx.db, q.EventsGetParams(organization_id=ctx.org, id=event_id)) |
| backend/src/kotorelay/operations/metrics/record_view/functions.py:62 | q.events_insert(ctx.db, q.EventsInsertParams(id=event_id, organization_id=ctx.org, user_id=ctx.user.id, department_id=data.department_id, document_id=doc.id, answer_id=None, kind='view', outcome='viewed', created_at=now())) |
| backend/src/kotorelay/operations/metrics/record_view/functions.py:90 | bool(rows) |
| backend/src/kotorelay/operations/metrics/record_view/functions.py:29 | require(ctx.member(data.department_id), 'forbidden', 403) |
| backend/src/kotorelay/operations/metrics/record_view/functions.py:22 | require(bool(doc.latest_version_id)) |
| backend/src/kotorelay/operations/metrics/record_view/functions.py:41 | require(previous[0].document_id == doc.id and previous[0].department_id == data.department_id and (previous[0].kind == 'view'), 'idempotency_conflict', 409) |
| backend/src/kotorelay/operations/metrics/record_view/generated/queries.py:40 | db.query('operations/metrics/record_view/sql/001_events_get.sql', params.model_dump(), EventsGetRow) |
| backend/src/kotorelay/operations/metrics/record_view/generated/queries.py:62 | db.execute('operations/metrics/record_view/sql/002_events_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/metrics/record_view/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/metrics/record_view/router.py:37 | build_response(f.build_record_view_2()) |
| backend/src/kotorelay/operations/metrics/record_view/router.py:34 | build_response(f.build_record_view()) |
| backend/src/kotorelay/operations/system/authorization/functions.py:6 | operation == 'read' |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:63 | db.query('operations/system/authorization/sql/002_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:98 | db.query('operations/system/authorization/sql/003_documents_get.sql', params.model_dump(), DocumentsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:176 | db.query('operations/system/authorization/sql/006_memberships_list.sql', params.model_dump(), MembershipsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:194 | db.execute('operations/system/authorization/sql/007_organizations_fence.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:220 | db.query('operations/system/authorization/sql/008_organizations_get.sql', params.model_dump(), OrganizationsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:248 | db.query('operations/system/authorization/sql/009_users_list.sql', params.model_dump(), UsersListRow) |
