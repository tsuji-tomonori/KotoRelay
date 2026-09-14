<!-- 実装から生成。直接編集しない。入力SHA256: 0ce2ee5ffefd1f44a0c3da213ceff59dfb82649c9add5715e204664ffd05fd84 -->

# manifestを確認して承認・却下 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: manifestを確認して承認・却下。

**Headers**

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| Idempotency-Key | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "uuid", "title": "Idempotency-Key"} |


認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


**Path Parameters**

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| submission_id | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "uuid", "title": "Submission Id"} |


**Query Parameters**

該当する入力はありません。

**Data**

媒体: `application/json`

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| manifest_hash | string | 必須 | 型定義に説明なし | {"pattern": "^[0-9a-f]{64}$"} |
| decision | string | 必須 | 型定義に説明なし | {"enum": ["approved", "rejected"]} |
| reason | string | 任意 | 型定義に説明なし | {"maxLength": 2000, "default": ""} |


## 2. 正常系前提

認証・認可と型制約を満たすこと。以下は実装の検査条件と制御分岐です。条件の成立を一律に正常系とは扱いません。

| 実装箇所 | 検査条件 | 不成立時／分岐 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:43 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:50 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:103 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/context.py:110 | allowed | not_found | 404 |
| backend/src/kotorelay/context.py:64 | q.organizations_fence(self.db, q.OrganizationsFenceParams.model_validate(self.organization, from_attributes=True)) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/context.py:153 | not rows | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:156 | record.operation == operation and record.request_hash == digest(request.encode()) | 'idempotency_conflict' | 409 |
| backend/src/kotorelay/context.py:117 | not self.permission(doc.department_id, 'draft') | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:115 | bool(rows) and rows[0].document_id == doc.id | not_found | 404 |
| backend/src/kotorelay/context.py:119 | digest(version.manifest.encode()) == version.manifest_hash | 'integrity' | 503 |
| backend/src/kotorelay/context.py:118 | self.can_read(doc) and doc.latest_version_id == version.id | not_found | 404 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:60 | version.created_by != ctx.user.id | 'self_approval' | 403 |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:48 | submission.status == 'pending' | 'conflict' | 409 |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:74 | data.decision != 'rejected' or bool(data.reason.strip()) | 'reason_required' | 422 |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:26 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:67 | submission.manifest_hash == data.manifest_hash == version.manifest_hash | 'conflict' | 409 |
| backend/src/kotorelay/operations/reviews/decide_review/router.py:34 | cached | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/reviews/decide_review/router.py:43 | f.is_approved(data) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/reviews/decide_review/router.py:45 | f.is_newer_publication(previous, version) | then / else の実装分岐 | 制御フロー参照 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| kotorelay.operations.reviews.decide_review.generated.queries.documents_update | documents | UPDATE |
| kotorelay.operations.reviews.decide_review.generated.queries.outbox_insert | outbox | INSERT |
| kotorelay.operations.reviews.decide_review.generated.queries.submissions_get | submissions | SELECT |
| kotorelay.operations.reviews.decide_review.generated.queries.submissions_update | submissions | UPDATE |
| kotorelay.operations.reviews.decide_review.generated.queries.versions_get | versions | SELECT |
| kotorelay.operations.system.authorization.generated.queries.audit_insert | audit | INSERT |
| kotorelay.operations.system.authorization.generated.queries.departments_list | departments | SELECT |
| kotorelay.operations.system.authorization.generated.queries.documents_get | documents | SELECT |
| kotorelay.operations.system.authorization.generated.queries.idempotency_get | idempotency | SELECT |
| kotorelay.operations.system.authorization.generated.queries.idempotency_insert | idempotency | INSERT |
| kotorelay.operations.system.authorization.generated.queries.memberships_list | memberships | SELECT |
| kotorelay.operations.system.authorization.generated.queries.organizations_fence | organizations | UPDATE |
| kotorelay.operations.system.authorization.generated.queries.organizations_get | organizations | SELECT |
| kotorelay.operations.system.authorization.generated.queries.users_list | users | SELECT |
| kotorelay.operations.system.authorization.generated.queries.versions_get | versions | SELECT |

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
| organization_id | string | 必須 | 型定義に説明なし | {} |
| document_id | string | 必須 | 型定義に説明なし | {} |
| version_id | string | 必須 | 型定義に説明なし | {} |
| requested_by | string | 必須 | 型定義に説明なし | {} |
| status | string | 必須 | 型定義に説明なし | {} |
| manifest_hash | string | 必須 | 型定義に説明なし | {} |
| decided_by | string &#124; null | 必須 | 型定義に説明なし | {"anyOf": [{"type": "string"}, {"type": "null"}]} |
| reason | string | 必須 | 型定義に説明なし | {} |
| created_at | string | 必須 | 型定義に説明なし | {"format": "date-time"} |
| decided_at | string &#124; null | 必須 | 型定義に説明なし | {"anyOf": [{"type": "string", "format": "date-time"}, {"type": "null"}]} |


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
| backend/src/kotorelay/context.py:111 | doc |
| backend/src/kotorelay/context.py:161 | record.response |
| backend/src/kotorelay/context.py:154 | None |
| backend/src/kotorelay/context.py:121 | version |
| backend/src/kotorelay/context.py:23 | str(uuid4()) |
| backend/src/kotorelay/context.py:19 | datetime.now(UTC) |
| backend/src/kotorelay/context.py:27 | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| backend/src/kotorelay/objects.py:17 | hashlib.sha256(data).hexdigest() |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:43 | models.SubmissionsRow.model_validate_json(cached) |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:81 | submission.model_copy(update={'status': data.decision, 'reason': data.reason, 'decided_by': ctx.user.id, 'decided_at': now()}) |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:173 | ctx.fence() |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:33 | ctx.document(submission.document_id, 'review') |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:117 | q.documents_update(ctx.db, q.DocumentsUpdateParams.model_validate(doc.model_copy(update={'latest_version_id': version.id, 'revision': doc.revision + 1, 'updated_at': now()}), from_attributes=True)) |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:38 | ctx.idempotent_result(str(key), 'decide', request) |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:100 | bool(data.decision == 'approved') |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:110 | bool(not previous or previous[0].number < version.number) |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:136 | q.outbox_insert(ctx.db, q.OutboxInsertParams(id=new_id(), organization_id=ctx.org, document_id=doc.id, version_id=version.id, kind='index', status='pending', attempts=0, error_code='', created_at=now())) |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:60 | require(version.created_by != ctx.user.id, 'self_approval', 403) |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:161 | ctx.audit('review', doc.id, version.id, submission.status, updated.status, data.reason) |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:168 | ctx.remember(str(key), 'decide', request, updated.model_dump_json()) |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:48 | require(submission.status == 'pending', 'conflict', 409) |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:74 | require(data.decision != 'rejected' or bool(data.reason.strip()), 'reason_required', 422) |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:26 | require(bool(rows)) |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:19 | q.submissions_get(ctx.db, q.SubmissionsGetParams(organization_id=ctx.org, id=str(submission_id))) |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:93 | q.submissions_update(ctx.db, q.SubmissionsUpdateParams.model_validate(updated, from_attributes=True)) |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:67 | require(submission.manifest_hash == data.manifest_hash == version.manifest_hash, 'conflict', 409) |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:55 | ctx.version(doc, submission.version_id) |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:105 | q.versions_get(ctx.db, q.VersionsGetParams(organization_id=ctx.org, id=version_id)) |
| backend/src/kotorelay/operations/reviews/decide_review/generated/queries.py:36 | db.execute('operations/reviews/decide_review/sql/001_documents_update.sql', params.model_dump()) |
| backend/src/kotorelay/operations/reviews/decide_review/generated/queries.py:58 | db.execute('operations/reviews/decide_review/sql/002_outbox_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/reviews/decide_review/generated/queries.py:90 | db.query('operations/reviews/decide_review/sql/003_submissions_get.sql', params.model_dump(), SubmissionsGetRow) |
| backend/src/kotorelay/operations/reviews/decide_review/generated/queries.py:116 | db.execute('operations/reviews/decide_review/sql/004_submissions_update.sql', params.model_dump()) |
| backend/src/kotorelay/operations/reviews/decide_review/generated/queries.py:148 | db.query('operations/reviews/decide_review/sql/005_versions_get.sql', params.model_dump(), VersionsGetRow) |
| backend/src/kotorelay/operations/reviews/decide_review/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/reviews/decide_review/router.py:51 | build_response(updated) |
| backend/src/kotorelay/operations/reviews/decide_review/router.py:35 | build_response(f.build_decide_review(cached)) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:39 | db.execute('operations/system/authorization/sql/001_audit_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:63 | db.query('operations/system/authorization/sql/002_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:98 | db.query('operations/system/authorization/sql/003_documents_get.sql', params.model_dump(), DocumentsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:127 | db.query('operations/system/authorization/sql/004_idempotency_get.sql', params.model_dump(), IdempotencyGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:148 | db.execute('operations/system/authorization/sql/005_idempotency_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:176 | db.query('operations/system/authorization/sql/006_memberships_list.sql', params.model_dump(), MembershipsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:194 | db.execute('operations/system/authorization/sql/007_organizations_fence.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:220 | db.query('operations/system/authorization/sql/008_organizations_get.sql', params.model_dump(), OrganizationsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:248 | db.query('operations/system/authorization/sql/009_users_list.sql', params.model_dump(), UsersListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:280 | db.query('operations/system/authorization/sql/010_versions_get.sql', params.model_dump(), VersionsGetRow) |
