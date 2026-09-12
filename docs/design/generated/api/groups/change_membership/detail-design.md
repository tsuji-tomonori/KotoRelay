<!-- 実装から生成。直接編集しない。入力SHA256: 31de213f242d3d7bf0d4f5957d4ef327aaacb2267a973d8e0adce1f1531ac7e1 -->

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
| backend/src/kotorelay/context.py:40 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:43 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:53 | q.organizations_fence(self.db, self.organization) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/context.py:60 | m.department_id == department_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/groups/functions.py:41 | rows | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/groups/functions.py:30 | ctx.permission(data.department_id, 'manage') or ctx.user.operator | 'forbidden' | 403 |
| backend/src/kotorelay/operations/groups/functions.py:31 | bool(q.users_get(ctx.db, ctx.org, data.user_id)) | 'not_found' | 404 |
| backend/src/kotorelay/operations/groups/functions.py:32 | bool(q.departments_get(ctx.db, ctx.org, data.department_id)) | 'not_found' | 404 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| audit_insert | audit | INSERT |
| departments_get | departments | SELECT |
| departments_list | departments | SELECT |
| memberships_insert | memberships | INSERT |
| memberships_list | memberships | SELECT |
| memberships_update | memberships | UPDATE |
| organizations_fence | organizations | UPDATE |
| organizations_get | organizations | SELECT |
| users_get | users | SELECT |
| users_list | users | SELECT |

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
| backend/src/kotorelay/context.py:67 | False |
| backend/src/kotorelay/context.py:61 | {'author': m.can_author, 'review': m.can_review, 'manage': m.leader, 'draft': m.can_author or m.can_review}.get(operation, False) |
| backend/src/kotorelay/context.py:22 | str(uuid4()) |
| backend/src/kotorelay/context.py:18 | datetime.now(UTC) |
| backend/src/kotorelay/generated/queries.py:734 | db.execute('operations/system/sql/audit_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:423 | db.query('operations/groups/sql/departments_get.sql', {'organization_id': organization_id, 'id': id}, DepartmentsRow) |
| backend/src/kotorelay/generated/queries.py:437 | db.query('operations/groups/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/generated/queries.py:468 | db.execute('operations/groups/sql/memberships_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:473 | db.query('operations/groups/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/generated/queries.py:482 | db.execute('operations/groups/sql/memberships_update.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:487 | db.execute('operations/identity/sql/organizations_fence.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:492 | db.query('operations/identity/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/generated/queries.py:520 | db.query('operations/identity/sql/users_get.sql', {'organization_id': organization_id, 'id': id}, UsersRow) |
| backend/src/kotorelay/generated/queries.py:534 | db.query('operations/identity/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
| backend/src/kotorelay/operations/groups/functions.py:47 | row |
| backend/src/kotorelay/operations/groups/router.py:27 | f.change(ctx, data) |
