<!-- 実装から生成。直接編集しない。入力SHA256: 209f2912c47883d8fdc722aafdde6cf403dff105c2efced6770337a06a320dd2 -->

# manifestを確認して承認・却下 — detail-design

目的: manifestを確認して承認・却下。

入力はinterface帳票の型制約に従います。認可はサーバーの有効所属と権限から決まります。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## DB操作と入出力

| query | DB対象 | 処理 |
| --- | --- | --- |
| audit_insert | audit | INSERT |
| departments_list | departments | SELECT |
| documents_get | documents | SELECT |
| documents_update | documents | UPDATE |
| idempotency_get | idempotency | SELECT |
| idempotency_insert | idempotency | INSERT |
| memberships_list | memberships | SELECT |
| organizations_fence | organizations | UPDATE |
| organizations_get | organizations | SELECT |
| outbox_insert | outbox | INSERT |
| submissions_get | submissions | SELECT |
| submissions_update | submissions | UPDATE |
| users_list | users | SELECT |
| versions_get | versions | SELECT |

## 前提・正常／異常分岐

| 実装箇所 | 検査条件 | 不成立時／分岐 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:40 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:43 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:82 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/context.py:89 | allowed | not_found | 404 |
| backend/src/kotorelay/context.py:53 | q.organizations_fence(self.db, self.organization) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/context.py:129 | not rows | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:132 | record.operation == operation and record.request_hash == digest(request.encode()) | 'idempotency_conflict' | 409 |
| backend/src/kotorelay/context.py:96 | not self.permission(doc.department_id, 'draft') | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:94 | bool(rows) and rows[0].document_id == doc.id | not_found | 404 |
| backend/src/kotorelay/context.py:98 | digest(version.manifest.encode()) == version.manifest_hash | 'integrity' | 503 |
| backend/src/kotorelay/context.py:97 | self.can_read(doc) and doc.latest_version_id == version.id | not_found | 404 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/reviews/functions.py:43 | cached | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/reviews/functions.py:61 | data.decision == 'approved' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/reviews/functions.py:38 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/operations/reviews/functions.py:45 | submission.status == 'pending' | 'conflict' | 409 |
| backend/src/kotorelay/operations/reviews/functions.py:47 | version.created_by != ctx.user.id | 'self_approval' | 403 |
| backend/src/kotorelay/operations/reviews/functions.py:48 | submission.manifest_hash == data.manifest_hash == version.manifest_hash | 'conflict' | 409 |
| backend/src/kotorelay/operations/reviews/functions.py:51 | data.decision != 'rejected' or bool(data.reason.strip()) | 'reason_required' | 422 |
| backend/src/kotorelay/operations/reviews/functions.py:65 | not previous or previous[0].number < version.number | then / else の実装分岐 | 制御フロー参照 |

## 応答項目の取得元

| 実装箇所 | 返却式（DB行・変換結果・固定値） |
| --- | --- |
| backend/src/kotorelay/context.py:90 | doc |
| backend/src/kotorelay/context.py:137 | record.response |
| backend/src/kotorelay/context.py:130 | None |
| backend/src/kotorelay/context.py:100 | version |
| backend/src/kotorelay/context.py:22 | str(uuid4()) |
| backend/src/kotorelay/context.py:18 | datetime.now(UTC) |
| backend/src/kotorelay/context.py:26 | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| backend/src/kotorelay/generated/queries.py:734 | db.execute('operations/system/sql/audit_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:437 | db.query('operations/groups/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/generated/queries.py:331 | db.query('operations/documents/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/generated/queries.py:354 | db.execute('operations/documents/sql/documents_update.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:746 | db.query('operations/system/sql/idempotency_get.sql', {'organization_id': organization_id, 'id': id}, IdempotencyRow) |
| backend/src/kotorelay/generated/queries.py:755 | db.execute('operations/system/sql/idempotency_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:473 | db.query('operations/groups/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/generated/queries.py:487 | db.execute('operations/identity/sql/organizations_fence.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:492 | db.query('operations/identity/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/generated/queries.py:651 | db.execute('operations/indexing/sql/outbox_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:697 | db.query('operations/reviews/sql/submissions_get.sql', {'organization_id': organization_id, 'id': id}, SubmissionsRow) |
| backend/src/kotorelay/generated/queries.py:720 | db.execute('operations/reviews/sql/submissions_update.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:534 | db.query('operations/identity/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
| backend/src/kotorelay/generated/queries.py:400 | db.query('operations/documents/sql/versions_get.sql', {'organization_id': organization_id, 'id': id}, VersionsRow) |
| backend/src/kotorelay/objects.py:17 | hashlib.sha256(data).hexdigest() |
| backend/src/kotorelay/operations/reviews/functions.py:93 | updated |
| backend/src/kotorelay/operations/reviews/functions.py:44 | q.SubmissionsRow.model_validate_json(cached) |
| backend/src/kotorelay/operations/reviews/router.py:27 | f.decide(ctx, str(submission_id), data, str(key)) |

異常時: DB transactionがrollbackします。S3の内容ハッシュ実体は孤立し得るため、公開認可に使わず、保持期間後の削除処理で回収します。外部配送失敗はoutboxのerror_codeとattemptsへ記録します。