<!-- 実装から生成。直接編集しない。入力SHA256: 31de213f242d3d7bf0d4f5957d4ef327aaacb2267a973d8e0adce1f1531ac7e1 -->

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
| backend/src/kotorelay/context.py:40 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:43 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:70 | doc.status != 'active' or not self.memberships | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:72 | doc.visibility == 'organization' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:74 | self.member(doc.department_id) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:294 | bool(conversations) and conversations[0].user_id == ctx.user.id | not_found | 404 |
| backend/src/kotorelay/operations/chat/functions.py:275 | answer.user_id == ctx.user.id | not_found | 404 |
| backend/src/kotorelay/operations/chat/functions.py:30 | not docs | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:33 | not ctx.can_read(doc) or doc.latest_version_id != citation.version_id or doc.revision != citation.document_revision | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:41 | not versions or not chunks | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:44 | not (digest(version.manifest.encode()) == version.manifest_hash and version.document_id == doc.id and chunk.ready and (chunk.version_id == version.id) and (chunk.document_id == doc.id) and (chunk.manifest_hash == version.manifest_hash == citation.manifest_hash) and (chunk.sha256 == citation.chunk_hash)) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:59 | placements - {image.placement.id for image in manifest.images} | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:62 | image.placement.id in json.loads(chunk.placements) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/chat/functions.py:65 | not assets or not runs or (not runs[0].confirmed) or (runs[0].status != 'ready') | then / else の実装分岐 | 制御フロー参照 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

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
| backend/src/kotorelay/context.py:76 | doc.visibility == 'selected' and any((self.member(department) for department in json.loads(doc.shared_departments))) |
| backend/src/kotorelay/context.py:71 | False |
| backend/src/kotorelay/context.py:73 | True |
| backend/src/kotorelay/context.py:75 | True |
| backend/src/kotorelay/generated/queries.py:264 | db.query('operations/chat/sql/answers_list.sql', {'organization_id': organization_id}, AnswersRow) |
| backend/src/kotorelay/generated/queries.py:553 | db.query('operations/images/sql/assets_get.sql', {'organization_id': organization_id, 'id': id}, AssetsRow) |
| backend/src/kotorelay/generated/queries.py:609 | db.query('operations/indexing/sql/chunks_get.sql', {'organization_id': organization_id, 'id': id}, ChunksRow) |
| backend/src/kotorelay/generated/queries.py:284 | db.query('operations/chat/sql/conversations_get.sql', {'organization_id': organization_id, 'id': id}, ConversationsRow) |
| backend/src/kotorelay/generated/queries.py:437 | db.query('operations/groups/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/generated/queries.py:331 | db.query('operations/documents/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/generated/queries.py:473 | db.query('operations/groups/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/generated/queries.py:581 | db.query('operations/images/sql/ocr_runs_get.sql', {'organization_id': organization_id, 'id': id}, OcrRunsRow) |
| backend/src/kotorelay/generated/queries.py:492 | db.query('operations/identity/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/generated/queries.py:534 | db.query('operations/identity/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
| backend/src/kotorelay/generated/queries.py:400 | db.query('operations/documents/sql/versions_get.sql', {'organization_id': organization_id, 'id': id}, VersionsRow) |
| backend/src/kotorelay/objects.py:17 | hashlib.sha256(data).hexdigest() |
| backend/src/kotorelay/operations/chat/functions.py:295 | [present(ctx, a) for a in sorted(q.answers_list(ctx.db, ctx.org), key=lambda a: a.created_at) if a.conversation_id == conversation_id] |
| backend/src/kotorelay/operations/chat/functions.py:278 | AnswerView(id=answer.id, conversation_id=answer.conversation_id, question=ctx.objects.get(answer.question_key).decode(), answer=ctx.objects.get(answer.answer_key).decode() if valid else '権限または公開版が変更されたため、この回答は表示できません。', status=answer.status if valid else 'hidden', citations=evidence.citations if valid else [], model=answer.model, created_at=answer.created_at) |
| backend/src/kotorelay/operations/chat/functions.py:31 | False |
| backend/src/kotorelay/operations/chat/functions.py:38 | False |
| backend/src/kotorelay/operations/chat/functions.py:42 | False |
| backend/src/kotorelay/operations/chat/functions.py:53 | False |
| backend/src/kotorelay/operations/chat/functions.py:69 | True |
| backend/src/kotorelay/operations/chat/functions.py:60 | False |
| backend/src/kotorelay/operations/chat/functions.py:71 | False |
| backend/src/kotorelay/operations/chat/functions.py:66 | False |
| backend/src/kotorelay/operations/chat/router.py:23 | f.history(ctx, str(conversation_id)) |
