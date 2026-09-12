<!-- 実装から生成。直接編集しない。入力SHA256: e3cb305ddf380bd9917bab7f5404c8ac54c8511b8d91b58e7192aa0d5991c3cf -->

# 反映ジョブを再処理 — detail-design

目的: 反映ジョブを再処理。

入力はinterface帳票の型制約に従います。認可はサーバーの有効所属と権限から決まります。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## DB操作と入出力

| query | DB対象 | 処理 |
| --- | --- | --- |
| answers_list | answers | SELECT |
| assets_delete | assets | DELETE |
| assets_get | assets | SELECT |
| assets_list | assets | SELECT |
| chunks_delete | chunks | DELETE |
| chunks_insert | chunks | INSERT |
| chunks_list | chunks | SELECT |
| chunks_update | chunks | UPDATE |
| departments_list | departments | SELECT |
| documents_get | documents | SELECT |
| documents_list | documents | SELECT |
| drafts_delete | drafts | DELETE |
| drafts_list | drafts | SELECT |
| memberships_list | memberships | SELECT |
| ocr_runs_delete | ocr_runs | DELETE |
| ocr_runs_get | ocr_runs | SELECT |
| ocr_runs_list | ocr_runs | SELECT |
| organizations_fence | organizations | UPDATE |
| organizations_get | organizations | SELECT |
| outbox_get | outbox | SELECT |
| outbox_update | outbox | UPDATE |
| users_list | users | SELECT |
| versions_get | versions | SELECT |
| versions_list | versions | SELECT |

## 前提・正常／異常分岐

| 実装箇所 | 検査条件 | 不成立時／分岐 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:40 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:43 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:53 | q.organizations_fence(self.db, self.organization) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:40 | doc.latest_version_id != job.version_id or not job.version_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:50 | len(stale) > 100 | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:52 | doc.status != 'active' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:70 | len(parts) <= 300 | 'limit' | 422 |
| backend/src/kotorelay/operations/indexing/functions.py:87 | chunk.id in previous | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:92 | len(actual) == len(parts) and engine.verify([c.id for c in actual]) | 'integrity' | 503 |
| backend/src/kotorelay/operations/indexing/functions.py:170 | job.status in {'done', 'obsolete'} | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:165 | ctx.user.operator | 'forbidden' | 403 |
| backend/src/kotorelay/operations/indexing/functions.py:167 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/operations/indexing/functions.py:169 | job.attempts < 5 | 'limit' | 429 |
| backend/src/kotorelay/operations/indexing/functions.py:101 | doc.status != 'deleted' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:103 | (now() - job.created_at).total_seconds() < ctx.settings.retention_days * 86400 | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:148 | len(target_chunks) > 100 | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:153 | len(target_runs) > 100 | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:156 | asset.document_id == doc.id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:159 | draft.document_id == doc.id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:132 | row.document_id == doc.id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:134 | row.document_id in live | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:33 | buffer.strip() | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:21 | line.startswith('#') or len(buffer) + len(line) > 1200 | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:22 | buffer.strip() | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:25 | line.startswith('#') | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:29 | len(buffer) + len(part) > 1200 and buffer.strip() | then / else の実装分岐 | 制御フロー参照 |

## 応答項目の取得元

| 実装箇所 | 返却式（DB行・変換結果・固定値） |
| --- | --- |
| backend/src/kotorelay/context.py:18 | datetime.now(UTC) |
| backend/src/kotorelay/context.py:26 | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| backend/src/kotorelay/generated/queries.py:264 | db.query('operations/chat/sql/answers_list.sql', {'organization_id': organization_id}, AnswersRow) |
| backend/src/kotorelay/generated/queries.py:535 | db.execute('operations/images/sql/assets_delete.sql', {'organization_id': organization_id, 'id': id}) |
| backend/src/kotorelay/generated/queries.py:542 | db.query('operations/images/sql/assets_get.sql', {'organization_id': organization_id, 'id': id}, AssetsRow) |
| backend/src/kotorelay/generated/queries.py:556 | db.query('operations/images/sql/assets_list.sql', {'organization_id': organization_id}, AssetsRow) |
| backend/src/kotorelay/generated/queries.py:591 | db.execute('operations/indexing/sql/chunks_delete.sql', {'organization_id': organization_id, 'id': id}) |
| backend/src/kotorelay/generated/queries.py:607 | db.execute('operations/indexing/sql/chunks_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:612 | db.query('operations/indexing/sql/chunks_list.sql', {'organization_id': organization_id}, ChunksRow) |
| backend/src/kotorelay/generated/queries.py:619 | db.execute('operations/indexing/sql/chunks_update.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:426 | db.query('operations/groups/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/generated/queries.py:320 | db.query('operations/documents/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/generated/queries.py:334 | db.query('operations/documents/sql/documents_list.sql', {'organization_id': organization_id}, DocumentsRow) |
| backend/src/kotorelay/generated/queries.py:348 | db.execute('operations/documents/sql/drafts_delete.sql', {'organization_id': organization_id, 'id': id}) |
| backend/src/kotorelay/generated/queries.py:369 | db.query('operations/documents/sql/drafts_list.sql', {'organization_id': organization_id}, DraftsRow) |
| backend/src/kotorelay/generated/queries.py:462 | db.query('operations/groups/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/generated/queries.py:563 | db.execute('operations/images/sql/ocr_runs_delete.sql', {'organization_id': organization_id, 'id': id}) |
| backend/src/kotorelay/generated/queries.py:570 | db.query('operations/images/sql/ocr_runs_get.sql', {'organization_id': organization_id, 'id': id}, OcrRunsRow) |
| backend/src/kotorelay/generated/queries.py:584 | db.query('operations/images/sql/ocr_runs_list.sql', {'organization_id': organization_id}, OcrRunsRow) |
| backend/src/kotorelay/generated/queries.py:476 | db.execute('operations/identity/sql/organizations_fence.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:481 | db.query('operations/identity/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/generated/queries.py:631 | db.query('operations/indexing/sql/outbox_get.sql', {'organization_id': organization_id, 'id': id}, OutboxRow) |
| backend/src/kotorelay/generated/queries.py:652 | db.execute('operations/indexing/sql/outbox_update.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:523 | db.query('operations/identity/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
| backend/src/kotorelay/generated/queries.py:389 | db.query('operations/documents/sql/versions_get.sql', {'organization_id': organization_id, 'id': id}, VersionsRow) |
| backend/src/kotorelay/generated/queries.py:403 | db.query('operations/documents/sql/versions_list.sql', {'organization_id': organization_id}, VersionsRow) |
| backend/src/kotorelay/operations/indexing/functions.py:96 | 'done' |
| backend/src/kotorelay/operations/indexing/functions.py:41 | 'obsolete' |
| backend/src/kotorelay/operations/indexing/functions.py:51 | 'pending' |
| backend/src/kotorelay/operations/indexing/functions.py:53 | 'done' |
| backend/src/kotorelay/operations/indexing/functions.py:195 | updated |
| backend/src/kotorelay/operations/indexing/functions.py:171 | job |
| backend/src/kotorelay/operations/indexing/functions.py:161 | 'done' |
| backend/src/kotorelay/operations/indexing/functions.py:102 | 'obsolete' |
| backend/src/kotorelay/operations/indexing/functions.py:104 | 'retained' |
| backend/src/kotorelay/operations/indexing/functions.py:149 | 'pending' |
| backend/src/kotorelay/operations/indexing/functions.py:154 | 'pending' |
| backend/src/kotorelay/operations/indexing/functions.py:35 | chunks |
| backend/src/kotorelay/operations/indexing/router.py:21 | f.process(ctx, rt.engine, str(job_id)) |

異常時: DB transactionがrollbackします。S3の内容ハッシュ実体は孤立し得るため、公開認可に使わず、保持期間後の削除処理で回収します。外部配送失敗はoutboxのerror_codeとattemptsへ記録します。