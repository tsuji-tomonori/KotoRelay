<!-- 実装から生成。直接編集しない。入力SHA256: 209f2912c47883d8fdc722aafdde6cf403dff105c2efced6770337a06a320dd2 -->

# 最新承認版の根拠で回答 — detail-design

目的: 最新承認版の根拠で回答。

入力はinterface帳票の型制約に従います。認可はサーバーの有効所属と権限から決まります。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## DB操作と入出力

| query | DB対象 | 処理 |
| --- | --- | --- |
| answers_get | answers | SELECT |
| answers_insert | answers | INSERT |
| answers_list | answers | SELECT |
| assets_get | assets | SELECT |
| audit_insert | audit | INSERT |
| chunks_get | chunks | SELECT |
| chunks_list | chunks | SELECT |
| conversations_get | conversations | SELECT |
| conversations_insert | conversations | INSERT |
| departments_list | departments | SELECT |
| documents_get | documents | SELECT |
| documents_list | documents | SELECT |
| events_insert | events | INSERT |
| events_list | events | SELECT |
| idempotency_get | idempotency | SELECT |
| idempotency_insert | idempotency | INSERT |
| memberships_list | memberships | SELECT |
| ocr_runs_get | ocr_runs | SELECT |
| organizations_fence | organizations | UPDATE |
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
| backend/src/kotorelay/context.py:53 | q.organizations_fence(self.db, self.organization) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/context.py:129 | not rows | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:132 | record.operation == operation and record.request_hash == digest(request.encode()) | 'idempotency_conflict' | 409 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:217 | ctx.member(prepared.department_id) | 'forbidden' | 403 |
| backend/src/kotorelay/operations/chat/functions.py:78 | prior | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:103 | resumed is not None | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:186 | resumed is None | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:75 | ctx.member(data.department_id) | 'forbidden' | 403 |
| backend/src/kotorelay/operations/chat/functions.py:92 | resumed is not None or sum((1 for e in events if e.user_id == ctx.user.id and e.kind == 'question' and (e.created_at.date() == today))) < ctx.settings.max_questions_per_day | 'limit' | 429 |
| backend/src/kotorelay/operations/chat/functions.py:105 | data.conversation_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:134 | chunk.document_id not in docs or chunk.version_id != docs[chunk.document_id].latest_version_id or (not chunk.ready) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:140 | vector_keys is not None and chunk.id not in vector_keys | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:151 | score > 0 and (vector_keys is not None or score >= max(1, len(terms(data.question)) * 0.3)) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:173 | not validate_citation(ctx, citation) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:177 | len(images) + len(related) > ctx.settings.max_model_images | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:184 | len(citations) >= 5 | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:79 | prior[0].user_id == ctx.user.id and ctx.objects.get(prior[0].question_key).decode() == data.question and (prior[0].department_id == data.department_id) and (data.conversation_id is None or data.conversation_id == prior[0].conversation_id) | 'idempotency_conflict' | 409 |
| backend/src/kotorelay/operations/chat/functions.py:107 | bool(conversations) and conversations[0].user_id == ctx.user.id | not_found | 404 |
| backend/src/kotorelay/operations/chat/functions.py:109 | all((a.department_id == data.department_id for a in q.answers_list(ctx.db, ctx.org) if a.conversation_id == conversation_id)) | 'conversation_department' | 409 |
| backend/src/kotorelay/operations/chat/functions.py:275 | answer.user_id == ctx.user.id | not_found | 404 |
| backend/src/kotorelay/operations/chat/functions.py:30 | not docs | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:33 | not ctx.can_read(doc) or doc.latest_version_id != citation.version_id or doc.revision != citation.document_revision | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:41 | not versions or not chunks | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:44 | not (digest(version.manifest.encode()) == version.manifest_hash and version.document_id == doc.id and chunk.ready and (chunk.version_id == version.id) and (chunk.document_id == doc.id) and (chunk.manifest_hash == version.manifest_hash == citation.manifest_hash) and (chunk.sha256 == citation.chunk_hash)) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:59 | placements - {image.placement.id for image in manifest.images} | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:62 | image.placement.id in json.loads(chunk.placements) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:65 | not assets or not runs or (not runs[0].confirmed) or (runs[0].status != 'ready') | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/service.py:23 | prepared.citations | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/service.py:28 | prepared.citations | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/service.py:17 | exc.code != 'already_answered' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/service.py:26 | not all((f.validate_citation(ctx, c) for c in prepared.citations)) | then / else の実装分岐 | 制御フロー参照 |

## 応答項目の取得元

| 実装箇所 | 返却式（DB行・変換結果・固定値） |
| --- | --- |
| backend/src/kotorelay/context.py:76 | doc.visibility == 'selected' and any((self.member(department) for department in json.loads(doc.shared_departments))) |
| backend/src/kotorelay/context.py:71 | False |
| backend/src/kotorelay/context.py:73 | True |
| backend/src/kotorelay/context.py:75 | True |
| backend/src/kotorelay/context.py:137 | record.response |
| backend/src/kotorelay/context.py:130 | None |
| backend/src/kotorelay/context.py:56 | any((m.department_id == department_id for m in self.memberships)) |
| backend/src/kotorelay/context.py:22 | str(uuid4()) |
| backend/src/kotorelay/context.py:18 | datetime.now(UTC) |
| backend/src/kotorelay/context.py:26 | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| backend/src/kotorelay/engines.py:30 | {value[i:i + 2] for i in range(max(0, len(value) - 1))} &#124; set(re.findall('[a-z0-9]+', value)) |
| backend/src/kotorelay/generated/queries.py:250 | db.query('operations/chat/sql/answers_get.sql', {'organization_id': organization_id, 'id': id}, AnswersRow) |
| backend/src/kotorelay/generated/queries.py:259 | db.execute('operations/chat/sql/answers_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:264 | db.query('operations/chat/sql/answers_list.sql', {'organization_id': organization_id}, AnswersRow) |
| backend/src/kotorelay/generated/queries.py:553 | db.query('operations/images/sql/assets_get.sql', {'organization_id': organization_id, 'id': id}, AssetsRow) |
| backend/src/kotorelay/generated/queries.py:734 | db.execute('operations/system/sql/audit_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:609 | db.query('operations/indexing/sql/chunks_get.sql', {'organization_id': organization_id, 'id': id}, ChunksRow) |
| backend/src/kotorelay/generated/queries.py:623 | db.query('operations/indexing/sql/chunks_list.sql', {'organization_id': organization_id}, ChunksRow) |
| backend/src/kotorelay/generated/queries.py:284 | db.query('operations/chat/sql/conversations_get.sql', {'organization_id': organization_id, 'id': id}, ConversationsRow) |
| backend/src/kotorelay/generated/queries.py:293 | db.execute('operations/chat/sql/conversations_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:437 | db.query('operations/groups/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/generated/queries.py:331 | db.query('operations/documents/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/generated/queries.py:345 | db.query('operations/documents/sql/documents_list.sql', {'organization_id': organization_id}, DocumentsRow) |
| backend/src/kotorelay/generated/queries.py:677 | db.execute('operations/metrics/sql/events_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:682 | db.query('operations/metrics/sql/events_list.sql', {'organization_id': organization_id}, EventsRow) |
| backend/src/kotorelay/generated/queries.py:746 | db.query('operations/system/sql/idempotency_get.sql', {'organization_id': organization_id, 'id': id}, IdempotencyRow) |
| backend/src/kotorelay/generated/queries.py:755 | db.execute('operations/system/sql/idempotency_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:473 | db.query('operations/groups/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/generated/queries.py:581 | db.query('operations/images/sql/ocr_runs_get.sql', {'organization_id': organization_id, 'id': id}, OcrRunsRow) |
| backend/src/kotorelay/generated/queries.py:487 | db.execute('operations/identity/sql/organizations_fence.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:492 | db.query('operations/identity/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/generated/queries.py:534 | db.query('operations/identity/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
| backend/src/kotorelay/generated/queries.py:400 | db.query('operations/documents/sql/versions_get.sql', {'organization_id': organization_id, 'id': id}, VersionsRow) |
| backend/src/kotorelay/objects.py:17 | hashlib.sha256(data).hexdigest() |
| backend/src/kotorelay/operations/chat/functions.py:271 | present(ctx, row) |
| backend/src/kotorelay/operations/chat/functions.py:203 | Prepared(answer_id=answer_id, conversation_id=conversation_id, question=data.question, department_id=data.department_id, citations=citations, texts=texts, images=images) |
| backend/src/kotorelay/operations/chat/functions.py:278 | AnswerView(id=answer.id, conversation_id=answer.conversation_id, question=ctx.objects.get(answer.question_key).decode(), answer=ctx.objects.get(answer.answer_key).decode() if valid else '権限または公開版が変更されたため、この回答は表示できません。', status=answer.status if valid else 'hidden', citations=evidence.citations if valid else [], model=answer.model, created_at=answer.created_at) |
| backend/src/kotorelay/operations/chat/functions.py:31 | False |
| backend/src/kotorelay/operations/chat/functions.py:38 | False |
| backend/src/kotorelay/operations/chat/functions.py:42 | False |
| backend/src/kotorelay/operations/chat/functions.py:53 | False |
| backend/src/kotorelay/operations/chat/functions.py:69 | True |
| backend/src/kotorelay/operations/chat/functions.py:60 | False |
| backend/src/kotorelay/operations/chat/functions.py:71 | False |
| backend/src/kotorelay/operations/chat/functions.py:66 | False |
| backend/src/kotorelay/operations/chat/router.py:18 | service.ask(rt, subject, data, str(key)) |
| backend/src/kotorelay/operations/chat/service.py:34 | f.finalize(ctx, prepared, answer, rt.engine, failed) |
| backend/src/kotorelay/operations/chat/service.py:20 | f.present(ctx, q.answers_get(ctx.db, ctx.org, exc.message)[0]) |

異常時: DB transactionがrollbackします。S3の内容ハッシュ実体は孤立し得るため、公開認可に使わず、保持期間後の削除処理で回収します。外部配送失敗はoutboxのerror_codeとattemptsへ記録します。