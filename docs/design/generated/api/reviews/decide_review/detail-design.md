<!-- 実装から生成。直接編集しない。入力SHA256: 987c18a693c5fa5c9f59f732c65771f1c047c0829e22a5d72b689276aae93c56 -->

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
| backend/src/kotorelay/context.py:41 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:44 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:83 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/context.py:90 | allowed | not_found | 404 |
| backend/src/kotorelay/context.py:54 | q.organizations_fence(self.db, self.organization) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/context.py:130 | not rows | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:133 | record.operation == operation and record.request_hash == digest(request.encode()) | 'idempotency_conflict' | 409 |
| backend/src/kotorelay/context.py:97 | not self.permission(doc.department_id, 'draft') | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:95 | bool(rows) and rows[0].document_id == doc.id | not_found | 404 |
| backend/src/kotorelay/context.py:99 | digest(version.manifest.encode()) == version.manifest_hash | 'integrity' | 503 |
| backend/src/kotorelay/context.py:98 | self.can_read(doc) and doc.latest_version_id == version.id | not_found | 404 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:19 | cached | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:37 | data.decision == 'approved' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:14 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:21 | submission.status == 'pending' | 'conflict' | 409 |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:23 | version.created_by != ctx.user.id | 'self_approval' | 403 |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:24 | submission.manifest_hash == data.manifest_hash == version.manifest_hash | 'conflict' | 409 |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:27 | data.decision != 'rejected' or bool(data.reason.strip()) | 'reason_required' | 422 |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:41 | not previous or previous[0].number < version.number | then / else の実装分岐 | 制御フロー参照 |


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
| backend/src/kotorelay/context.py:91 | doc |
| backend/src/kotorelay/context.py:138 | record.response |
| backend/src/kotorelay/context.py:131 | None |
| backend/src/kotorelay/context.py:101 | version |
| backend/src/kotorelay/context.py:23 | str(uuid4()) |
| backend/src/kotorelay/context.py:19 | datetime.now(UTC) |
| backend/src/kotorelay/context.py:27 | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| backend/src/kotorelay/objects.py:17 | hashlib.sha256(data).hexdigest() |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:69 | updated |
| backend/src/kotorelay/operations/reviews/decide_review/functions.py:20 | models.SubmissionsRow.model_validate_json(cached) |
| backend/src/kotorelay/operations/reviews/decide_review/generated/queries.py:16 | db.execute('operations/reviews/decide_review/sql/documents_update.sql', row.model_dump()) |
| backend/src/kotorelay/operations/reviews/decide_review/generated/queries.py:21 | db.execute('operations/reviews/decide_review/sql/outbox_insert.sql', row.model_dump()) |
| backend/src/kotorelay/operations/reviews/decide_review/generated/queries.py:26 | db.query('operations/reviews/decide_review/sql/submissions_get.sql', {'organization_id': organization_id, 'id': id}, SubmissionsRow) |
| backend/src/kotorelay/operations/reviews/decide_review/generated/queries.py:35 | db.execute('operations/reviews/decide_review/sql/submissions_update.sql', row.model_dump()) |
| backend/src/kotorelay/operations/reviews/decide_review/generated/queries.py:42 | db.query('operations/reviews/decide_review/sql/versions_get.sql', {'organization_id': organization_id, 'id': id}, VersionsRow) |
| backend/src/kotorelay/operations/reviews/decide_review/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/reviews/decide_review/router.py:26 | build_response(f.decide(ctx, str(submission_id), data, str(key))) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:20 | db.execute('operations/system/authorization/sql/audit_insert.sql', row.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:25 | db.query('operations/system/authorization/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:34 | db.query('operations/system/authorization/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:43 | db.query('operations/system/authorization/sql/idempotency_get.sql', {'organization_id': organization_id, 'id': id}, IdempotencyRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:52 | db.execute('operations/system/authorization/sql/idempotency_insert.sql', row.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:59 | db.query('operations/system/authorization/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:68 | db.execute('operations/system/authorization/sql/organizations_fence.sql', row.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:75 | db.query('operations/system/authorization/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:84 | db.query('operations/system/authorization/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:93 | db.query('operations/system/authorization/sql/versions_get.sql', {'organization_id': organization_id, 'id': id}, VersionsRow) |
