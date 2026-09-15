<!-- 実装から生成。直接編集しない。入力SHA256: 065f3a0aaa159ee25b4b54797ae13bebd5e0deb08cdd00f2becc4afbe26e1319 -->

# 現行認可で会話履歴を再表示 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: 現行認可で会話履歴を再表示。

**Headers**

該当する入力はありません。

認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


**Path Parameters**

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| conversation_id | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "uuid", "title": "Conversation Id"} |


**Query Parameters**

該当する入力はありません。

**Data**

リクエスト本文はありません。

## 2. 正常系前提

認証・認可と型制約を満たすこと。以下は実装の検査条件と制御分岐です。条件の成立を一律に正常系とは扱いません。

| 実装箇所 | 検査条件 | 不成立時／分岐 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:45 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:52 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:95 | doc.status != 'active' or not self.memberships | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:97 | doc.visibility == 'organization' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:99 | self.member(doc.department_id) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/chat_history/functions.py:27 | bool(conversations) and conversations[0].user_id == ctx.user.id | not_found | 404 |
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
| kotorelay.operations.chat.chat_history.generated.queries.answers_list | answers | SELECT |
| kotorelay.operations.chat.chat_history.generated.queries.conversations_get | conversations | SELECT |
| kotorelay.operations.chat.shared.generated.queries.assets_get | assets | SELECT |
| kotorelay.operations.chat.shared.generated.queries.chunks_get | chunks | SELECT |
| kotorelay.operations.chat.shared.generated.queries.documents_get | documents | SELECT |
| kotorelay.operations.chat.shared.generated.queries.ocr_runs_get | ocr_runs | SELECT |
| kotorelay.operations.chat.shared.generated.queries.versions_get | versions | SELECT |
| kotorelay.operations.system.authorization.generated.queries.departments_list | departments | SELECT |
| kotorelay.operations.system.authorization.generated.queries.memberships_list | memberships | SELECT |
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
| [].id | string | 必須 | 型定義に説明なし | {} |
| [].conversation_id | string | 必須 | 型定義に説明なし | {} |
| [].question | string | 必須 | 型定義に説明なし | {} |
| [].answer | string | 必須 | 型定義に説明なし | {} |
| [].status | string | 必須 | 型定義に説明なし | {} |
| [].citations | array<Citation> | 必須 | 型定義に説明なし | {} |
| [].citations[].version_number | integer &#124; null | 任意 | 型定義に説明なし | {"anyOf": [{"type": "integer"}, {"type": "null"}]} |
| [].citations[].has_images | boolean | 任意 | 型定義に説明なし | {"default": false} |
| [].citations[].document_id | string | 必須 | 型定義に説明なし | {} |
| [].citations[].version_id | string | 必須 | 型定義に説明なし | {} |
| [].citations[].chunk_id | string | 必須 | 型定義に説明なし | {} |
| [].citations[].title | string | 必須 | 型定義に説明なし | {} |
| [].citations[].heading | string | 必須 | 型定義に説明なし | {} |
| [].citations[].manifest_hash | string | 必須 | 型定義に説明なし | {} |
| [].citations[].chunk_hash | string | 必須 | 型定義に説明なし | {} |
| [].citations[].document_revision | integer | 必須 | 型定義に説明なし | {} |
| [].model | string | 必須 | 型定義に説明なし | {} |
| [].created_at | string | 必須 | 型定義に説明なし | {"format": "date-time"} |


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
| backend/src/kotorelay/objects.py:17 | hashlib.sha256(data).hexdigest() |
| backend/src/kotorelay/operational_logging.py:150 | OperationalLogContext(request_id=REQUEST_ID.get(), exception_type=type(error).__name__, status=None, code=(error.code if isinstance(error, Problem) else 'external_failure') if message_id == MessageId.INDEX_FAILED else None, message=CATALOG[message_id].response) |
| backend/src/kotorelay/operations/chat/chat_history/functions.py:46 | answer.conversation_id == str(conversation_id) |
| backend/src/kotorelay/operations/chat/chat_history/functions.py:18 | q.conversations_get(ctx.db, q.ConversationsGetParams(organization_id=ctx.org, id=str(conversation_id))) |
| backend/src/kotorelay/operations/chat/chat_history/functions.py:27 | require(bool(conversations) and conversations[0].user_id == ctx.user.id) |
| backend/src/kotorelay/operations/chat/chat_history/functions.py:34 | [present(ctx, a) for a in sorted(q.answers_list(ctx.db, q.AnswersListParams(organization_id=ctx.org)), key=lambda a: a.created_at) if belongs_to_conversation(a, conversation_id)] |
| backend/src/kotorelay/operations/chat/chat_history/generated/queries.py:42 | db.query('operations/chat/chat_history/sql/001_answers_list.sql', params.model_dump(), AnswersListRow) |
| backend/src/kotorelay/operations/chat/chat_history/generated/queries.py:67 | db.query('operations/chat/chat_history/sql/002_conversations_get.sql', params.model_dump(), ConversationsGetRow) |
| backend/src/kotorelay/operations/chat/chat_history/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/chat/chat_history/router.py:28 | build_response(f.select_chat_history(ctx, conversation_id)) |
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
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:63 | db.query('operations/system/authorization/sql/002_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:176 | db.query('operations/system/authorization/sql/006_memberships_list.sql', params.model_dump(), MembershipsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:220 | db.query('operations/system/authorization/sql/008_organizations_get.sql', params.model_dump(), OrganizationsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:248 | db.query('operations/system/authorization/sql/009_users_list.sql', params.model_dump(), UsersListRow) |
