<!-- 実装から生成。直接編集しない。入力SHA256: 209f2912c47883d8fdc722aafdde6cf403dff105c2efced6770337a06a320dd2 -->

# 部署の所属権限を変更 — detail-design

目的: 部署の所属権限を変更。

入力はinterface帳票の型制約に従います。認可はサーバーの有効所属と権限から決まります。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## DB操作と入出力

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

## 前提・正常／異常分岐

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

## 応答項目の取得元

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

異常時: DB transactionがrollbackします。S3の内容ハッシュ実体は孤立し得るため、公開認可に使わず、保持期間後の削除処理で回収します。外部配送失敗はoutboxのerror_codeとattemptsへ記録します。