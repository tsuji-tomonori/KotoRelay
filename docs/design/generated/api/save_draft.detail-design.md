<!-- 実装から生成。直接編集しない。入力SHA256: f4209c4ed7b292c6ed57aa300cf25000f8931a1f59b1fb43cfeb436b1d949dbe -->

# 競合を検出して下書きを保存 — detail-design

目的: 競合を検出して下書きを保存。

入力はinterface帳票の型制約に従います。認可はサーバーの有効所属と権限から決まります。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## DB操作と入出力

| query | DB対象 | 処理 |
| --- | --- | --- |
| assets_get | assets | SELECT |
| departments_list | departments | SELECT |
| documents_get | documents | SELECT |
| documents_update | documents | UPDATE |
| drafts_list | drafts | SELECT |
| drafts_update | drafts | UPDATE |
| memberships_list | memberships | SELECT |
| ocr_runs_get | ocr_runs | SELECT |
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
| backend/src/kotorelay/operations/documents/functions.py:111 | row.revision == data.revision | 'conflict' | 409 |
| backend/src/kotorelay/operations/documents/functions.py:93 | len({p.id for p in data.placements}) == len(data.placements) | 'invalid_placement' | 422 |
| backend/src/kotorelay/operations/documents/functions.py:97 | bool(assets) and bool(runs) | 'invalid_placement' | 422 |
| backend/src/kotorelay/operations/documents/functions.py:98 | assets[0].document_id == doc.id and runs[0].asset_id == assets[0].id and (runs[0].document_id == doc.id) and (placement.offset <= len(data.body)) | 'invalid_placement' | 422 |

## 応答項目の取得元

| 実装箇所 | 返却式（DB行・変換結果・固定値） |
| --- | --- |
| backend/src/kotorelay/context.py:90 | doc |
| backend/src/kotorelay/context.py:18 | datetime.now(UTC) |
| backend/src/kotorelay/generated/queries.py:542 | db.query('operations/images/sql/assets_get.sql', {'organization_id': organization_id, 'id': id}, AssetsRow) |
| backend/src/kotorelay/generated/queries.py:426 | db.query('operations/groups/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/generated/queries.py:320 | db.query('operations/documents/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/generated/queries.py:343 | db.execute('operations/documents/sql/documents_update.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:369 | db.query('operations/documents/sql/drafts_list.sql', {'organization_id': organization_id}, DraftsRow) |
| backend/src/kotorelay/generated/queries.py:376 | db.execute('operations/documents/sql/drafts_update.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:462 | db.query('operations/groups/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/generated/queries.py:570 | db.query('operations/images/sql/ocr_runs_get.sql', {'organization_id': organization_id, 'id': id}, OcrRunsRow) |
| backend/src/kotorelay/generated/queries.py:476 | db.execute('operations/identity/sql/organizations_fence.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:481 | db.query('operations/identity/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/generated/queries.py:523 | db.query('operations/identity/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
| backend/src/kotorelay/operations/documents/functions.py:84 | {'document': doc, 'body': ctx.objects.get(row.body_key, row.body_hash).decode(), 'revision': row.revision, 'placements': json.loads(row.placements)} |
| backend/src/kotorelay/operations/documents/functions.py:133 | draft(ctx, doc.id) |
| backend/src/kotorelay/operations/documents/router.py:40 | f.save(ctx, str(document_id), data) |

異常時: DB transactionがrollbackします。S3の内容ハッシュ実体は孤立し得るため、公開認可に使わず、保持期間後の削除処理で回収します。外部配送失敗はoutboxのerror_codeとattemptsへ記録します。