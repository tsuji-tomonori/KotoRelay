<!-- 実装から生成。直接編集しない。入力SHA256: f4209c4ed7b292c6ed57aa300cf25000f8931a1f59b1fb43cfeb436b1d949dbe -->

# 現行認可で会話履歴を再表示 — detail-design

目的: 現行認可で会話履歴を再表示。

入力はinterface帳票の型制約に従います。認可はサーバーの有効所属と権限から決まります。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## DB操作と入出力

| query | DB対象 | 処理 |
| --- | --- | --- |
| answers_list | answers | SELECT |
| assets_get | assets | SELECT |
| chunks_get | chunks | SELECT |
| conversations_get | conversations | SELECT |
| departments_list | departments | SELECT |
| documents_get | documents | SELECT |
| memberships_list | memberships | SELECT |
| ocr_runs_get | ocr_runs | SELECT |
| organizations_get | organizations | SELECT |
| users_list | users | SELECT |
| versions_get | versions | SELECT |

## 前提・正常／異常分岐

| 実装箇所 | 検査条件 | 不成立時／分岐 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:40 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:43 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:70 | doc.status != 'active' or not self.memberships | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:72 | doc.visibility == 'organization' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:74 | self.member(doc.department_id) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:283 | bool(conversations) and conversations[0].user_id == ctx.user.id | not_found | 404 |
| backend/src/kotorelay/operations/chat/functions.py:264 | answer.user_id == ctx.user.id | not_found | 404 |
| backend/src/kotorelay/operations/chat/functions.py:30 | not docs | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:33 | not ctx.can_read(doc) or doc.latest_version_id != citation.version_id or doc.revision != citation.document_revision | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:41 | not versions or not chunks | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:44 | not (digest(version.manifest.encode()) == version.manifest_hash and version.document_id == doc.id and chunk.ready and (chunk.version_id == version.id) and (chunk.document_id == doc.id) and (chunk.manifest_hash == version.manifest_hash == citation.manifest_hash) and (chunk.sha256 == citation.chunk_hash)) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:59 | placements - {image.placement.id for image in manifest.images} | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:62 | image.placement.id in json.loads(chunk.placements) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:65 | not assets or not runs or (not runs[0].confirmed) or (runs[0].status != 'ready') | then / else の実装分岐 | 制御フロー参照 |

## 応答項目の取得元

| 実装箇所 | 返却式（DB行・変換結果・固定値） |
| --- | --- |
| backend/src/kotorelay/context.py:76 | doc.visibility == 'selected' and any((self.member(department) for department in json.loads(doc.shared_departments))) |
| backend/src/kotorelay/context.py:71 | False |
| backend/src/kotorelay/context.py:73 | True |
| backend/src/kotorelay/context.py:75 | True |
| backend/src/kotorelay/generated/queries.py:264 | db.query('operations/chat/sql/answers_list.sql', {'organization_id': organization_id}, AnswersRow) |
| backend/src/kotorelay/generated/queries.py:542 | db.query('operations/images/sql/assets_get.sql', {'organization_id': organization_id, 'id': id}, AssetsRow) |
| backend/src/kotorelay/generated/queries.py:598 | db.query('operations/indexing/sql/chunks_get.sql', {'organization_id': organization_id, 'id': id}, ChunksRow) |
| backend/src/kotorelay/generated/queries.py:284 | db.query('operations/chat/sql/conversations_get.sql', {'organization_id': organization_id, 'id': id}, ConversationsRow) |
| backend/src/kotorelay/generated/queries.py:426 | db.query('operations/groups/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/generated/queries.py:320 | db.query('operations/documents/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/generated/queries.py:462 | db.query('operations/groups/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/generated/queries.py:570 | db.query('operations/images/sql/ocr_runs_get.sql', {'organization_id': organization_id, 'id': id}, OcrRunsRow) |
| backend/src/kotorelay/generated/queries.py:481 | db.query('operations/identity/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/generated/queries.py:523 | db.query('operations/identity/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
| backend/src/kotorelay/generated/queries.py:389 | db.query('operations/documents/sql/versions_get.sql', {'organization_id': organization_id, 'id': id}, VersionsRow) |
| backend/src/kotorelay/objects.py:17 | hashlib.sha256(data).hexdigest() |
| backend/src/kotorelay/operations/chat/functions.py:284 | [present(ctx, a) for a in sorted(q.answers_list(ctx.db, ctx.org), key=lambda a: a.created_at) if a.conversation_id == conversation_id] |
| backend/src/kotorelay/operations/chat/functions.py:267 | AnswerView(id=answer.id, conversation_id=answer.conversation_id, question=ctx.objects.get(answer.question_key).decode(), answer=ctx.objects.get(answer.answer_key).decode() if valid else '権限または公開版が変更されたため、この回答は表示できません。', status=answer.status if valid else 'hidden', citations=evidence.citations if valid else [], model=answer.model, created_at=answer.created_at) |
| backend/src/kotorelay/operations/chat/functions.py:31 | False |
| backend/src/kotorelay/operations/chat/functions.py:38 | False |
| backend/src/kotorelay/operations/chat/functions.py:42 | False |
| backend/src/kotorelay/operations/chat/functions.py:53 | False |
| backend/src/kotorelay/operations/chat/functions.py:69 | True |
| backend/src/kotorelay/operations/chat/functions.py:60 | False |
| backend/src/kotorelay/operations/chat/functions.py:71 | False |
| backend/src/kotorelay/operations/chat/functions.py:66 | False |
| backend/src/kotorelay/operations/chat/router.py:23 | f.history(ctx, str(conversation_id)) |

異常時: DB transactionがrollbackします。S3の内容ハッシュ実体は孤立し得るため、公開認可に使わず、保持期間後の削除処理で回収します。外部配送失敗はoutboxのerror_codeとattemptsへ記録します。