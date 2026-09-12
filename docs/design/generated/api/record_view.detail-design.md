<!-- 実装から生成。直接編集しない。入力SHA256: e3cb305ddf380bd9917bab7f5404c8ac54c8511b8d91b58e7192aa0d5991c3cf -->

# 実閲覧を一意IDで記録 — detail-design

目的: 実閲覧を一意IDで記録。

入力はinterface帳票の型制約に従います。認可はサーバーの有効所属と権限から決まります。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## DB操作と入出力

| query | DB対象 | 処理 |
| --- | --- | --- |
| departments_list | departments | SELECT |
| documents_get | documents | SELECT |
| events_get | events | SELECT |
| events_insert | events | INSERT |
| memberships_list | memberships | SELECT |
| organizations_fence | organizations | UPDATE |
| organizations_get | organizations | SELECT |
| users_list | users | SELECT |

## 前提・正常／異常分岐

| 実装箇所 | 検査条件 | 不成立時／分岐 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:40 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:43 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:82 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/context.py:89 | allowed | not_found | 404 |
| backend/src/kotorelay/context.py:53 | q.organizations_fence(self.db, self.organization) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/metrics/functions.py:18 | previous | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/metrics/functions.py:14 | bool(doc.latest_version_id) | not_found | 404 |
| backend/src/kotorelay/operations/metrics/functions.py:15 | ctx.member(data.department_id) | 'forbidden' | 403 |
| backend/src/kotorelay/operations/metrics/functions.py:19 | previous[0].document_id == doc.id and previous[0].department_id == data.department_id and (previous[0].kind == 'view') | 'idempotency_conflict' | 409 |

## 応答項目の取得元

| 実装箇所 | 返却式（DB行・変換結果・固定値） |
| --- | --- |
| backend/src/kotorelay/context.py:90 | doc |
| backend/src/kotorelay/context.py:56 | any((m.department_id == department_id for m in self.memberships)) |
| backend/src/kotorelay/context.py:18 | datetime.now(UTC) |
| backend/src/kotorelay/context.py:26 | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| backend/src/kotorelay/generated/queries.py:426 | db.query('operations/groups/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/generated/queries.py:320 | db.query('operations/documents/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/generated/queries.py:657 | db.query('operations/metrics/sql/events_get.sql', {'organization_id': organization_id, 'id': id}, EventsRow) |
| backend/src/kotorelay/generated/queries.py:666 | db.execute('operations/metrics/sql/events_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:462 | db.query('operations/groups/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/generated/queries.py:476 | db.execute('operations/identity/sql/organizations_fence.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:481 | db.query('operations/identity/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/generated/queries.py:523 | db.query('operations/identity/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
| backend/src/kotorelay/operations/metrics/functions.py:42 | {'recorded': True} |
| backend/src/kotorelay/operations/metrics/functions.py:26 | {'recorded': False} |
| backend/src/kotorelay/operations/metrics/router.py:17 | f.view(ctx, str(document_id), data) |

異常時: DB transactionがrollbackします。S3の内容ハッシュ実体は孤立し得るため、公開認可に使わず、保持期間後の削除処理で回収します。外部配送失敗はoutboxのerror_codeとattemptsへ記録します。