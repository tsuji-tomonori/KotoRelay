<!-- 実装から生成。直接編集しない。入力SHA256: f473ec4902a9e7cc973e702d4fbb05a99ce8c26a324da9a1f4592aab94dbd60c -->

# 部署の所属権限を変更 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: 部署の所属権限を変更。

**Headers**

該当する入力はありません。

認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


**Path Parameters**

該当する入力はありません。

**Query Parameters**

該当する入力はありません。

**Data**

媒体: `application/json`

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| user_id | string | 必須 | 型定義に説明なし | {"pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"} |
| department_id | string | 必須 | 型定義に説明なし | {"pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"} |
| leader | boolean | 任意 | 型定義に説明なし | {"default": false} |
| can_author | boolean | 任意 | 型定義に説明なし | {"default": false} |
| can_review | boolean | 任意 | 型定義に説明なし | {"default": false} |
| active | boolean | 任意 | 型定義に説明なし | {"default": true} |


## 2. 正常系前提

認証・認可と型制約を満たすこと。以下は実装の検査条件と制御分岐です。条件の成立を一律に正常系とは扱いません。

| 実装箇所 | 検査条件 | 不成立時／分岐 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:45 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:52 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:67 | q.organizations_fence(self.db, q.OrganizationsFenceParams.model_validate(self.organization, from_attributes=True)) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/context.py:84 | m.department_id == department_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/groups/change_membership/functions.py:17 | ctx.permission(data.department_id, 'manage') or ctx.user.operator | 'forbidden' | 403 |
| backend/src/kotorelay/operations/groups/change_membership/functions.py:35 | bool(q.departments_get(ctx.db, q.DepartmentsGetParams(organization_id=ctx.org, id=data.department_id))) | 'not_found' | 404 |
| backend/src/kotorelay/operations/groups/change_membership/functions.py:24 | bool(q.users_get(ctx.db, q.UsersGetParams(organization_id=ctx.org, id=data.user_id))) | 'not_found' | 404 |
| backend/src/kotorelay/operations/groups/change_membership/router.py:30 | f.has_existing_membership(rows) | then / else の実装分岐 | 制御フロー参照 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| kotorelay.operations.groups.change_membership.generated.queries.departments_get | departments | SELECT |
| kotorelay.operations.groups.change_membership.generated.queries.memberships_insert | memberships | INSERT |
| kotorelay.operations.groups.change_membership.generated.queries.memberships_list | memberships | SELECT |
| kotorelay.operations.groups.change_membership.generated.queries.memberships_update | memberships | UPDATE |
| kotorelay.operations.groups.change_membership.generated.queries.users_get | users | SELECT |
| kotorelay.operations.system.authorization.generated.queries.audit_insert | audit | INSERT |
| kotorelay.operations.system.authorization.generated.queries.departments_list | departments | SELECT |
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
| user_id | string | 必須 | 型定義に説明なし | {} |
| leader | boolean | 必須 | 型定義に説明なし | {} |
| can_author | boolean | 必須 | 型定義に説明なし | {} |
| can_review | boolean | 必須 | 型定義に説明なし | {} |
| active | boolean | 必須 | 型定義に説明なし | {} |


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
| backend/src/kotorelay/context.py:91 | False |
| backend/src/kotorelay/context.py:85 | {'author': m.can_author, 'review': m.can_review, 'manage': m.leader, 'draft': m.can_author or m.can_review}.get(operation, False) |
| backend/src/kotorelay/context.py:24 | str(uuid4()) |
| backend/src/kotorelay/context.py:20 | datetime.now(UTC) |
| backend/src/kotorelay/operations/groups/change_membership/functions.py:63 | models.MembershipsRow(id=rows[0].id if has_existing_membership(rows) else new_id(), organization_id=ctx.org, **data.model_dump()) |
| backend/src/kotorelay/operations/groups/change_membership/functions.py:95 | ctx.fence() |
| backend/src/kotorelay/operations/groups/change_membership/functions.py:100 | bool(rows) |
| backend/src/kotorelay/operations/groups/change_membership/functions.py:79 | q.memberships_insert(ctx.db, q.MembershipsInsertParams.model_validate(row, from_attributes=True)) |
| backend/src/kotorelay/operations/groups/change_membership/functions.py:72 | q.memberships_update(ctx.db, q.MembershipsUpdateParams.model_validate(row, from_attributes=True)) |
| backend/src/kotorelay/operations/groups/change_membership/functions.py:88 | ctx.audit('membership', before=str(rows[0].active) if rows else '', after=str(row.active)) |
| backend/src/kotorelay/operations/groups/change_membership/functions.py:17 | require(ctx.permission(data.department_id, 'manage') or ctx.user.operator, 'forbidden', 403) |
| backend/src/kotorelay/operations/groups/change_membership/functions.py:35 | require(bool(q.departments_get(ctx.db, q.DepartmentsGetParams(organization_id=ctx.org, id=data.department_id))), 'not_found', 404) |
| backend/src/kotorelay/operations/groups/change_membership/functions.py:24 | require(bool(q.users_get(ctx.db, q.UsersGetParams(organization_id=ctx.org, id=data.user_id))), 'not_found', 404) |
| backend/src/kotorelay/operations/groups/change_membership/functions.py:50 | [m for m in q.memberships_list(ctx.db, q.MembershipsListParams(organization_id=ctx.org)) if m.user_id == data.user_id and m.department_id == data.department_id] |
| backend/src/kotorelay/operations/groups/change_membership/generated/queries.py:35 | db.query('operations/groups/change_membership/sql/001_departments_get.sql', params.model_dump(), DepartmentsGetRow) |
| backend/src/kotorelay/operations/groups/change_membership/generated/queries.py:58 | db.execute('operations/groups/change_membership/sql/002_memberships_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/groups/change_membership/generated/queries.py:86 | db.query('operations/groups/change_membership/sql/003_memberships_list.sql', params.model_dump(), MembershipsListRow) |
| backend/src/kotorelay/operations/groups/change_membership/generated/queries.py:109 | db.execute('operations/groups/change_membership/sql/004_memberships_update.sql', params.model_dump()) |
| backend/src/kotorelay/operations/groups/change_membership/generated/queries.py:136 | db.query('operations/groups/change_membership/sql/005_users_get.sql', params.model_dump(), UsersGetRow) |
| backend/src/kotorelay/operations/groups/change_membership/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/groups/change_membership/router.py:36 | build_response(row) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:39 | db.execute('operations/system/authorization/sql/001_audit_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:63 | db.query('operations/system/authorization/sql/002_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:176 | db.query('operations/system/authorization/sql/006_memberships_list.sql', params.model_dump(), MembershipsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:194 | db.execute('operations/system/authorization/sql/007_organizations_fence.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:220 | db.query('operations/system/authorization/sql/008_organizations_get.sql', params.model_dump(), OrganizationsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:248 | db.query('operations/system/authorization/sql/009_users_list.sql', params.model_dump(), UsersListRow) |
