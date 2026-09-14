<!-- 実装から生成。直接編集しない。入力SHA256: ac3b8a89c10fb6f4c0a9456ea4fb59251414105722d4188a0beaca0d8b493f26 -->

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
| backend/src/kotorelay/context.py:45 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:52 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:95 | doc.status != 'active' or not self.memberships | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:97 | doc.visibility == 'organization' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:99 | self.member(doc.department_id) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:67 | q.organizations_fence(self.db, q.OrganizationsFenceParams.model_validate(self.organization, from_attributes=True)) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/context.py:162 | not rows | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:165 | record.operation == operation and record.request_hash == digest(request.encode()) | 'idempotency_conflict' | 409 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:86 | resumed is not None or sum((1 for e in events if e.user_id == ctx.user.id and e.kind == 'question' and (e.created_at.date() == today))) < ctx.settings.max_questions_per_day | 'limit' | 429 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:112 | bool(conversations) and conversations[0].user_id == ctx.user.id | not_found | 404 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:271 | ctx.member(prepared.department_id) | 'forbidden' | 403 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:47 | ctx.member(data.department_id) | 'forbidden' | 403 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:119 | all((a.department_id == data.department_id for a in q.answers_list(ctx.db, q.AnswersListParams(organization_id=ctx.org)) if a.conversation_id == conversation_id)) | 'conversation_department' | 409 |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:59 | prior[0].user_id == ctx.user.id and ctx.objects.get(prior[0].question_key).decode() == data.question and (prior[0].department_id == data.department_id) and (data.conversation_id is None or data.conversation_id == prior[0].conversation_id) | 'idempotency_conflict' | 409 |
| backend/src/kotorelay/operations/chat/ask_question/router.py:120 | f.has_answer_evidence(prepared) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/router.py:124 | f.has_answer_evidence(prepared) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/router.py:42 | f.has_previous_answer(prior) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/router.py:50 | f.has_prepared_conversation(resumed) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/router.py:100 | f.is_new_question(resumed) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/router.py:114 | f.is_unhandled_problem(exc) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/router.py:122 | not f.has_valid_evidence(ctx, prepared.citations) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/router.py:52 | f.has_requested_conversation(data) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/router.py:65 | f.is_unavailable_chunk(docs, chunk) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/router.py:67 | f.is_outside_search_results(vector_keys, chunk) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/router.py:78 | f.has_sufficient_relevance(score, vector_keys, data) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/router.py:87 | not evidence_functions.validate_citation(ctx, citation) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/router.py:91 | f.exceeds_image_limit(images, related, ctx) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/ask_question/router.py:98 | f.has_enough_citations(citations) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/shared/functions.py:78 | answer.user_id == ctx.user.id | not_found | 404 |
| backend/src/kotorelay/operations/chat/shared/functions.py:21 | not docs | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/shared/functions.py:24 | not ctx.can_read(doc) or doc.latest_version_id != citation.version_id or doc.revision != citation.document_revision | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/shared/functions.py:34 | not versions or not chunks | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/shared/functions.py:37 | not (digest(version.manifest.encode()) == version.manifest_hash and version.document_id == doc.id and chunk.ready and (chunk.version_id == version.id) and (chunk.document_id == doc.id) and (chunk.manifest_hash == version.manifest_hash == citation.manifest_hash) and (chunk.sha256 == citation.chunk_hash)) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/shared/functions.py:52 | placements - {image.placement.id for image in manifest.images} | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/shared/functions.py:55 | is_cited_image(image, chunk) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/shared/functions.py:63 | not assets or not runs or (not runs[0].confirmed) or (runs[0].status != 'ready') | then / else の実装分岐 | 制御フロー参照 |


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
| backend/src/kotorelay/context.py:101 | doc.visibility == 'selected' and any((self.member(department) for department in json.loads(doc.shared_departments))) |
| backend/src/kotorelay/context.py:96 | False |
| backend/src/kotorelay/context.py:98 | True |
| backend/src/kotorelay/context.py:100 | True |
| backend/src/kotorelay/context.py:170 | record.response |
| backend/src/kotorelay/context.py:163 | None |
| backend/src/kotorelay/context.py:79 | any((m.department_id == department_id for m in self.memberships)) |
| backend/src/kotorelay/context.py:24 | str(uuid4()) |
| backend/src/kotorelay/context.py:20 | datetime.now(UTC) |
| backend/src/kotorelay/context.py:28 | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| backend/src/kotorelay/engines.py:30 | {value[i:i + 2] for i in range(max(0, len(value) - 1))} &#124; set(re.findall('[a-z0-9]+', value)) |
| backend/src/kotorelay/objects.py:17 | hashlib.sha256(data).hexdigest() |
| backend/src/kotorelay/operational_logging.py:150 | OperationalLogContext(request_id=REQUEST_ID.get(), exception_type=type(error).__name__, status=None, code=(error.code if isinstance(error, Problem) else 'external_failure') if message_id == MessageId.INDEX_FAILED else None, message=CATALOG[message_id].response) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:32 | q.answers_get(ctx.db, q.AnswersGetParams(organization_id=ctx.org, id=exc.message)) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:52 | q.answers_get(ctx.db, q.AnswersGetParams(organization_id=ctx.org, id=answer_id)) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:300 | q.answers_insert(ctx.db, q.AnswersInsertParams.model_validate(row, from_attributes=True)) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:217 | q.assets_get(ctx.db, q.AssetsGetParams(organization_id=ctx.org, id=image.placement.asset_id)) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:283 | models.AnswersRow(id=prepared.answer_id, organization_id=ctx.org, conversation_id=prepared.conversation_id, user_id=ctx.user.id, department_id=prepared.department_id, question_key=ctx.objects.put(prepared.question.encode()), answer_key=ctx.objects.put(text.encode()), evidence=Evidence(citations=citations).model_dump_json(), status=status, model=engine.name, created_at=now()) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:373 | shared_schemas.Citation(document_id=doc.id, version_id=version.id, version_number=version.number, has_images=bool(json.loads(chunk.placements)), chunk_id=chunk.id, title=version.title, heading=chunk.heading, manifest_hash=version.manifest_hash, chunk_hash=chunk.sha256, document_revision=doc.revision) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:266 | ctx.fence() |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:158 | q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org)) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:325 | {c.document_id for c in citations} |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:103 | q.conversations_get(ctx.db, q.ConversationsGetParams(organization_id=ctx.org, id=conversation_id)) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:132 | q.conversations_insert(ctx.db, q.ConversationsInsertParams(id=conversation_id, organization_id=ctx.org, user_id=ctx.user.id, created_at=now())) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:37 | prepared.model_copy(update={'citations': [], 'texts': [], 'images': []}) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:86 | require(resumed is not None or sum((1 for e in events if e.user_id == ctx.user.id and e.kind == 'question' and (e.created_at.date() == today))) < ctx.settings.max_questions_per_day, 'limit', 429) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:241 | q.events_insert(ctx.db, q.EventsInsertParams(id=answer_id, organization_id=ctx.org, user_id=ctx.user.id, department_id=data.department_id, document_id=None, answer_id=None, kind='question', outcome='accepted', created_at=now())) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:307 | q.events_insert(ctx.db, q.EventsInsertParams(id=stable_id(row.id + 'outcome'), organization_id=ctx.org, user_id=ctx.user.id, department_id=prepared.department_id, document_id=None, answer_id=row.id, kind='outcome', outcome=status, created_at=now())) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:336 | q.events_insert(ctx.db, q.EventsInsertParams(id=stable_id(row.id + document_id), organization_id=ctx.org, user_id=ctx.user.id, department_id=prepared.department_id, document_id=document_id, answer_id=row.id, kind='contribution', outcome=status, created_at=now())) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:76 | q.events_list(ctx.db, q.EventsListParams(organization_id=ctx.org)) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:210 | bool(len(images) + len(related) > ctx.settings.max_model_images) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:71 | ctx.idempotent_result(key, 'ask', request) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:42 | rt.engine.generate(prepared.question, prepared.texts, prepared.images) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:425 | bool(prepared.citations) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:231 | bool(len(citations) >= 5) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:415 | conversation_id is not None |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:410 | bool(rows) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:420 | bool(data.conversation_id) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:184 | bool(score > 0 and (vector_keys is not None or score >= max(1, len(terms(data.question)) * 0.3))) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:432 | all((evidence_functions.validate_citation(ctx, citation) for citation in citations)) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:236 | bool(resumed is None) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:172 | bool(vector_keys is not None and chunk.id not in vector_keys) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:163 | bool(chunk.document_id not in docs or chunk.version_id != docs[chunk.document_id].latest_version_id or (not chunk.ready)) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:27 | bool(exc.code != 'already_answered') |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:177 | ctx.objects.get(chunk.body_key, chunk.sha256).decode() |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:226 | ctx.objects.get(asset.object_key, image.image_hash) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:142 | {d.id: d for d in q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org)) if d.latest_version_id and ctx.can_read(d)} |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:196 | Manifest.model_validate_json(version.manifest) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:391 | sorted(scored, key=lambda item: (-item[0], item[1].id))[:10] |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:354 | ctx.audit('answer', after=status) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:261 | ctx.remember(key, 'ask', request, conversation_id) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:112 | require(bool(conversations) and conversations[0].user_id == ctx.user.id) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:271 | require(ctx.member(prepared.department_id), 'forbidden', 403) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:47 | require(ctx.member(data.department_id), 'forbidden', 403) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:119 | require(all((a.department_id == data.department_id for a in q.answers_list(ctx.db, q.AnswersListParams(organization_id=ctx.org)) if a.conversation_id == conversation_id)), 'conversation_department', 409) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:399 | (status, evidence if status == 'answered' else [], answer if status == 'answered' else '現在利用できる根拠が不足しているため、回答を保留しました。') |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:359 | float(len(terms(question) & terms(text))) if uses_local_scoring(vector_keys) else float(len(typing.cast(list[str], vector_keys)) - typing.cast(list[str], vector_keys).index(chunk_id)) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:153 | engine.search(data.question, list(docs)) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:203 | [i for i in manifest.images if i.placement.id in json.loads(chunk.placements)] |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:437 | vector_keys is None |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:59 | require(prior[0].user_id == ctx.user.id and ctx.objects.get(prior[0].question_key).decode() == data.question and (prior[0].department_id == data.department_id) and (data.conversation_id is None or data.conversation_id == prior[0].conversation_id), 'idempotency_conflict', 409) |
| backend/src/kotorelay/operations/chat/ask_question/functions.py:191 | q.versions_get(ctx.db, q.VersionsGetParams(organization_id=ctx.org, id=chunk.version_id)) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:48 | db.query('operations/chat/ask_question/sql/001_answers_get.sql', params.model_dump(), AnswersGetRow) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:72 | db.execute('operations/chat/ask_question/sql/002_answers_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:103 | db.query('operations/chat/ask_question/sql/003_answers_list.sql', params.model_dump(), AnswersListRow) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:134 | db.query('operations/chat/ask_question/sql/004_assets_get.sql', params.model_dump(), AssetsGetRow) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:164 | db.query('operations/chat/ask_question/sql/005_chunks_list.sql', params.model_dump(), ChunksListRow) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:189 | db.query('operations/chat/ask_question/sql/006_conversations_get.sql', params.model_dump(), ConversationsGetRow) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:208 | db.execute('operations/chat/ask_question/sql/007_conversations_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:240 | db.query('operations/chat/ask_question/sql/008_documents_list.sql', params.model_dump(), DocumentsListRow) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:264 | db.execute('operations/chat/ask_question/sql/009_events_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:291 | db.query('operations/chat/ask_question/sql/010_events_list.sql', params.model_dump(), EventsListRow) |
| backend/src/kotorelay/operations/chat/ask_question/generated/queries.py:323 | db.query('operations/chat/ask_question/sql/011_versions_get.sql', params.model_dump(), VersionsGetRow) |
| backend/src/kotorelay/operations/chat/ask_question/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/chat/ask_question/router.py:146 | build_response(present(ctx, row)) |
| backend/src/kotorelay/operations/chat/ask_question/router.py:117 | build_response(present(ctx, f.answers_get(ctx, exc)[0])) |
| backend/src/kotorelay/operations/chat/shared/functions.py:102 | valid |
| backend/src/kotorelay/operations/chat/shared/functions.py:97 | image.placement.id in json.loads(chunk.placements) |
| backend/src/kotorelay/operations/chat/shared/functions.py:81 | AnswerView(id=answer.id, conversation_id=answer.conversation_id, question=ctx.objects.get(answer.question_key).decode(), answer=ctx.objects.get(answer.answer_key).decode() if has_valid_evidence(valid) else '権限または公開版が変更されたため、この回答は表示できません。', status=answer.status if has_valid_evidence(valid) else 'hidden', citations=evidence.citations if has_valid_evidence(valid) else [], model=answer.model, created_at=answer.created_at) |
| backend/src/kotorelay/operations/chat/shared/functions.py:22 | False |
| backend/src/kotorelay/operations/chat/shared/functions.py:29 | False |
| backend/src/kotorelay/operations/chat/shared/functions.py:35 | False |
| backend/src/kotorelay/operations/chat/shared/functions.py:46 | False |
| backend/src/kotorelay/operations/chat/shared/functions.py:67 | True |
| backend/src/kotorelay/operations/chat/shared/functions.py:53 | False |
| backend/src/kotorelay/operations/chat/shared/functions.py:73 | False |
| backend/src/kotorelay/operations/chat/shared/functions.py:64 | False |
| backend/src/kotorelay/operations/chat/shared/generated/queries.py:45 | db.query('operations/chat/shared/sql/001_assets_get.sql', params.model_dump(), AssetsGetRow) |
| backend/src/kotorelay/operations/chat/shared/generated/queries.py:76 | db.query('operations/chat/shared/sql/002_chunks_get.sql', params.model_dump(), ChunksGetRow) |
| backend/src/kotorelay/operations/chat/shared/generated/queries.py:109 | db.query('operations/chat/shared/sql/003_documents_get.sql', params.model_dump(), DocumentsGetRow) |
| backend/src/kotorelay/operations/chat/shared/generated/queries.py:140 | db.query('operations/chat/shared/sql/004_ocr_runs_get.sql', params.model_dump(), OcrRunsGetRow) |
| backend/src/kotorelay/operations/chat/shared/generated/queries.py:172 | db.query('operations/chat/shared/sql/005_versions_get.sql', params.model_dump(), VersionsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:39 | db.execute('operations/system/authorization/sql/001_audit_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:63 | db.query('operations/system/authorization/sql/002_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:127 | db.query('operations/system/authorization/sql/004_idempotency_get.sql', params.model_dump(), IdempotencyGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:148 | db.execute('operations/system/authorization/sql/005_idempotency_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:176 | db.query('operations/system/authorization/sql/006_memberships_list.sql', params.model_dump(), MembershipsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:194 | db.execute('operations/system/authorization/sql/007_organizations_fence.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:220 | db.query('operations/system/authorization/sql/008_organizations_get.sql', params.model_dump(), OrganizationsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:248 | db.query('operations/system/authorization/sql/009_users_list.sql', params.model_dump(), UsersListRow) |
