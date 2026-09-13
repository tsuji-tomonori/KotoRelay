<!-- 実装から生成。直接編集しない。入力SHA256: 987c18a693c5fa5c9f59f732c65771f1c047c0829e22a5d72b689276aae93c56 -->

# 最新承認版の根拠で回答 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: 最新承認版の根拠で回答。

**Headers**

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| Idempotency-Key | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "uuid", "title": "Idempotency-Key"} |


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
| question | string | 必須 | 型定義に説明なし | {"maxLength": 2000, "minLength": 1} |
| department_id | string | 必須 | 型定義に説明なし | {"pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"} |
| conversation_id | string &#124; null | 任意 | 型定義に説明なし | {"anyOf": [{"type": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"}, {"type": "null"}]} |


## 2. 正常系前提

認証・認可と型制約を満たすこと。以下は実装の検査条件と制御分岐です。条件の成立を一律に正常系とは扱いません。

| 実装箇所 | 検査条件 | 不成立時／分岐 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:41 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:44 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:71 | doc.status != 'active' or not self.memberships | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:73 | doc.visibility == 'organization' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:75 | self.member(doc.department_id) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:54 | q.organizations_fence(self.db, self.organization) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/context.py:130 | not rows | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:133 | record.operation == operation and record.request_hash == digest(request.encode()) | 'idempotency_conflict' | 409 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:243 | prepared.citations | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:248 | prepared.citations | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:237 | exc.code != 'already_answered' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:246 | not all((validate_citation(ctx, c) for c in prepared.citations)) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:175 | ctx.member(prepared.department_id) | 'forbidden' | 403 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:36 | prior | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:61 | resumed is not None | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:144 | resumed is None | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:33 | ctx.member(data.department_id) | 'forbidden' | 403 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:50 | resumed is not None or sum((1 for e in events if e.user_id == ctx.user.id and e.kind == 'question' and (e.created_at.date() == today))) < ctx.settings.max_questions_per_day | 'limit' | 429 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:63 | data.conversation_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:92 | chunk.document_id not in docs or chunk.version_id != docs[chunk.document_id].latest_version_id or (not chunk.ready) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:98 | vector_keys is not None and chunk.id not in vector_keys | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:109 | score > 0 and (vector_keys is not None or score >= max(1, len(terms(data.question)) * 0.3)) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:131 | not validate_citation(ctx, citation) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:135 | len(images) + len(related) > ctx.settings.max_model_images | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:142 | len(citations) >= 5 | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:37 | prior[0].user_id == ctx.user.id and ctx.objects.get(prior[0].question_key).decode() == data.question and (prior[0].department_id == data.department_id) and (data.conversation_id is None or data.conversation_id == prior[0].conversation_id) | 'idempotency_conflict' | 409 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:65 | bool(conversations) and conversations[0].user_id == ctx.user.id | not_found | 404 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:67 | all((a.department_id == data.department_id for a in q.answers_list(ctx.db, ctx.org) if a.conversation_id == conversation_id)) | 'conversation_department' | 409 |
| backend/src/kotorelay/operations/chat/shared/functions.py:62 | answer.user_id == ctx.user.id | not_found | 404 |
| backend/src/kotorelay/operations/chat/shared/functions.py:17 | not docs | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/shared/functions.py:20 | not ctx.can_read(doc) or doc.latest_version_id != citation.version_id or doc.revision != citation.document_revision | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/shared/functions.py:28 | not versions or not chunks | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/shared/functions.py:31 | not (digest(version.manifest.encode()) == version.manifest_hash and version.document_id == doc.id and chunk.ready and (chunk.version_id == version.id) and (chunk.document_id == doc.id) and (chunk.manifest_hash == version.manifest_hash == citation.manifest_hash) and (chunk.sha256 == citation.chunk_hash)) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/shared/functions.py:46 | placements - {image.placement.id for image in manifest.images} | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/shared/functions.py:49 | image.placement.id in json.loads(chunk.placements) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/shared/functions.py:52 | not assets or not runs or (not runs[0].confirmed) or (runs[0].status != 'ready') | then / else の実装分岐 | 制御フロー参照 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| kotorelay.operations.chat.ask_question.generated.queries.answers_get | answers | SELECT |
| kotorelay.operations.chat.ask_question.generated.queries.answers_insert | answers | INSERT |
| kotorelay.operations.chat.ask_question.generated.queries.answers_list | answers | SELECT |
| kotorelay.operations.chat.ask_question.generated.queries.assets_get | assets | SELECT |
| kotorelay.operations.chat.ask_question.generated.queries.chunks_list | chunks | SELECT |
| kotorelay.operations.chat.ask_question.generated.queries.conversations_get | conversations | SELECT |
| kotorelay.operations.chat.ask_question.generated.queries.conversations_insert | conversations | INSERT |
| kotorelay.operations.chat.ask_question.generated.queries.documents_list | documents | SELECT |
| kotorelay.operations.chat.ask_question.generated.queries.events_insert | events | INSERT |
| kotorelay.operations.chat.ask_question.generated.queries.events_list | events | SELECT |
| kotorelay.operations.chat.ask_question.generated.queries.versions_get | versions | SELECT |
| kotorelay.operations.chat.shared.generated.queries.assets_get | assets | SELECT |
| kotorelay.operations.chat.shared.generated.queries.chunks_get | chunks | SELECT |
| kotorelay.operations.chat.shared.generated.queries.documents_get | documents | SELECT |
| kotorelay.operations.chat.shared.generated.queries.ocr_runs_get | ocr_runs | SELECT |
| kotorelay.operations.chat.shared.generated.queries.versions_get | versions | SELECT |
| kotorelay.operations.system.authorization.generated.queries.audit_insert | audit | INSERT |
| kotorelay.operations.system.authorization.generated.queries.departments_list | departments | SELECT |
| kotorelay.operations.system.authorization.generated.queries.idempotency_get | idempotency | SELECT |
| kotorelay.operations.system.authorization.generated.queries.idempotency_insert | idempotency | INSERT |
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
| conversation_id | string | 必須 | 型定義に説明なし | {} |
| question | string | 必須 | 型定義に説明なし | {} |
| answer | string | 必須 | 型定義に説明なし | {} |
| status | string | 必須 | 型定義に説明なし | {} |
| citations | array<Citation> | 必須 | 型定義に説明なし | {} |
| citations[].version_number | integer &#124; null | 任意 | 型定義に説明なし | {"anyOf": [{"type": "integer"}, {"type": "null"}]} |
| citations[].has_images | boolean | 任意 | 型定義に説明なし | {"default": false} |
| citations[].document_id | string | 必須 | 型定義に説明なし | {} |
| citations[].version_id | string | 必須 | 型定義に説明なし | {} |
| citations[].chunk_id | string | 必須 | 型定義に説明なし | {} |
| citations[].title | string | 必須 | 型定義に説明なし | {} |
| citations[].heading | string | 必須 | 型定義に説明なし | {} |
| citations[].manifest_hash | string | 必須 | 型定義に説明なし | {} |
| citations[].chunk_hash | string | 必須 | 型定義に説明なし | {} |
| citations[].document_revision | integer | 必須 | 型定義に説明なし | {} |
| model | string | 必須 | 型定義に説明なし | {} |
| created_at | string | 必須 | 型定義に説明なし | {"format": "date-time"} |


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
| backend/src/kotorelay/context.py:77 | doc.visibility == 'selected' and any((self.member(department) for department in json.loads(doc.shared_departments))) |
| backend/src/kotorelay/context.py:72 | False |
| backend/src/kotorelay/context.py:74 | True |
| backend/src/kotorelay/context.py:76 | True |
| backend/src/kotorelay/context.py:138 | record.response |
| backend/src/kotorelay/context.py:131 | None |
| backend/src/kotorelay/context.py:57 | any((m.department_id == department_id for m in self.memberships)) |
| backend/src/kotorelay/context.py:23 | str(uuid4()) |
| backend/src/kotorelay/context.py:19 | datetime.now(UTC) |
| backend/src/kotorelay/context.py:27 | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| backend/src/kotorelay/engines.py:30 | {value[i:i + 2] for i in range(max(0, len(value) - 1))} &#124; set(re.findall('[a-z0-9]+', value)) |
| backend/src/kotorelay/objects.py:17 | hashlib.sha256(data).hexdigest() |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:254 | finalize(ctx, prepared, answer, rt.engine, failed) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:240 | present(ctx, q.answers_get(ctx.db, ctx.org, exc.message)[0]) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:229 | present(ctx, row) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:161 | Prepared(answer_id=answer_id, conversation_id=conversation_id, question=data.question, department_id=data.department_id, citations=citations, texts=texts, images=images) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:19 | db.query('operations/chat/ask_question/sql/answers_get.sql', {'organization_id': organization_id, 'id': id}, AnswersRow) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:28 | db.execute('operations/chat/ask_question/sql/answers_insert.sql', row.model_dump()) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:33 | db.query('operations/chat/ask_question/sql/answers_list.sql', {'organization_id': organization_id}, AnswersRow) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:42 | db.query('operations/chat/ask_question/sql/assets_get.sql', {'organization_id': organization_id, 'id': id}, AssetsRow) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:51 | db.query('operations/chat/ask_question/sql/chunks_list.sql', {'organization_id': organization_id}, ChunksRow) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:60 | db.query('operations/chat/ask_question/sql/conversations_get.sql', {'organization_id': organization_id, 'id': id}, ConversationsRow) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:69 | db.execute('operations/chat/ask_question/sql/conversations_insert.sql', row.model_dump()) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:74 | db.query('operations/chat/ask_question/sql/documents_list.sql', {'organization_id': organization_id}, DocumentsRow) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:83 | db.execute('operations/chat/ask_question/sql/events_insert.sql', row.model_dump()) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:88 | db.query('operations/chat/ask_question/sql/events_list.sql', {'organization_id': organization_id}, EventsRow) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:97 | db.query('operations/chat/ask_question/sql/versions_get.sql', {'organization_id': organization_id, 'id': id}, VersionsRow) |
| backend/src/kotorelay/operations/chat/ask_question/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/chat/ask_question/router.py:24 | build_response(f.ask(rt, subject, data, str(key))) |
| backend/src/kotorelay/operations/chat/shared/functions.py:65 | AnswerView(id=answer.id, conversation_id=answer.conversation_id, question=ctx.objects.get(answer.question_key).decode(), answer=ctx.objects.get(answer.answer_key).decode() if valid else '権限または公開版が変更されたため、この回答は表示できません。', status=answer.status if valid else 'hidden', citations=evidence.citations if valid else [], model=answer.model, created_at=answer.created_at) |
| backend/src/kotorelay/operations/chat/shared/functions.py:18 | False |
| backend/src/kotorelay/operations/chat/shared/functions.py:25 | False |
| backend/src/kotorelay/operations/chat/shared/functions.py:29 | False |
| backend/src/kotorelay/operations/chat/shared/functions.py:40 | False |
| backend/src/kotorelay/operations/chat/shared/functions.py:56 | True |
| backend/src/kotorelay/operations/chat/shared/functions.py:47 | False |
| backend/src/kotorelay/operations/chat/shared/functions.py:58 | False |
| backend/src/kotorelay/operations/chat/shared/functions.py:53 | False |
| backend/src/kotorelay/operations/chat/shared/generated/queries.py:17 | db.query('operations/chat/shared/sql/assets_get.sql', {'organization_id': organization_id, 'id': id}, AssetsRow) |
| backend/src/kotorelay/operations/chat/shared/generated/queries.py:26 | db.query('operations/chat/shared/sql/chunks_get.sql', {'organization_id': organization_id, 'id': id}, ChunksRow) |
| backend/src/kotorelay/operations/chat/shared/generated/queries.py:35 | db.query('operations/chat/shared/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/operations/chat/shared/generated/queries.py:44 | db.query('operations/chat/shared/sql/ocr_runs_get.sql', {'organization_id': organization_id, 'id': id}, OcrRunsRow) |
| backend/src/kotorelay/operations/chat/shared/generated/queries.py:53 | db.query('operations/chat/shared/sql/versions_get.sql', {'organization_id': organization_id, 'id': id}, VersionsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:20 | db.execute('operations/system/authorization/sql/audit_insert.sql', row.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:25 | db.query('operations/system/authorization/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:43 | db.query('operations/system/authorization/sql/idempotency_get.sql', {'organization_id': organization_id, 'id': id}, IdempotencyRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:52 | db.execute('operations/system/authorization/sql/idempotency_insert.sql', row.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:59 | db.query('operations/system/authorization/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:68 | db.execute('operations/system/authorization/sql/organizations_fence.sql', row.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:75 | db.query('operations/system/authorization/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:84 | db.query('operations/system/authorization/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
