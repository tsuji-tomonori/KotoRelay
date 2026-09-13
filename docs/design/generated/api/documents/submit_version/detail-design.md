<!-- 実装から生成。直接編集しない。入力SHA256: 987c18a693c5fa5c9f59f732c65771f1c047c0829e22a5d72b689276aae93c56 -->

# 版を確定して承認申請 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: 版を確定して承認申請。

**Headers**

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| Idempotency-Key | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "uuid", "title": "Idempotency-Key"} |


認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


**Path Parameters**

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| document_id | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "uuid", "title": "Document Id"} |


**Query Parameters**

該当する入力はありません。

**Data**

媒体: `application/json`

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| revision | integer | 必須 | 型定義に説明なし | {"minimum": 1.0} |


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
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:20 | cached | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:23 | row.revision == data.revision | 'conflict' | 409 |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:29 | ocr.confirmed and ocr.status == 'ready' | 'ocr_unconfirmed' | 409 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| kotorelay.operations.documents.submit_version.generated.queries.assets_get | assets | SELECT |
| kotorelay.operations.documents.submit_version.generated.queries.documents_update | documents | UPDATE |
| kotorelay.operations.documents.submit_version.generated.queries.drafts_list | drafts | SELECT |
| kotorelay.operations.documents.submit_version.generated.queries.ocr_runs_get | ocr_runs | SELECT |
| kotorelay.operations.documents.submit_version.generated.queries.submissions_insert | submissions | INSERT |
| kotorelay.operations.documents.submit_version.generated.queries.versions_insert | versions | INSERT |
| kotorelay.operations.system.authorization.generated.queries.audit_insert | audit | INSERT |
| kotorelay.operations.system.authorization.generated.queries.departments_list | departments | SELECT |
| kotorelay.operations.system.authorization.generated.queries.documents_get | documents | SELECT |
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
| 201 | Successful Response | application/json |
| 422 | Validation Error | application/json |

##### `201` Successful Response

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| id | string | 必須 | 型定義に説明なし | {} |
| organization_id | string | 必須 | 型定義に説明なし | {} |
| document_id | string | 必須 | 型定義に説明なし | {} |
| number | integer | 必須 | 型定義に説明なし | {} |
| title | string | 必須 | 型定義に説明なし | {} |
| body_key | string | 必須 | 型定義に説明なし | {} |
| body_hash | string | 必須 | 型定義に説明なし | {} |
| manifest | string | 必須 | 型定義に説明なし | {} |
| manifest_hash | string | 必須 | 型定義に説明なし | {} |
| created_by | string | 必須 | 型定義に説明なし | {} |
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
| backend/src/kotorelay/context.py:91 | doc |
| backend/src/kotorelay/context.py:138 | record.response |
| backend/src/kotorelay/context.py:131 | None |
| backend/src/kotorelay/context.py:23 | str(uuid4()) |
| backend/src/kotorelay/context.py:19 | datetime.now(UTC) |
| backend/src/kotorelay/context.py:27 | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| backend/src/kotorelay/objects.py:17 | hashlib.sha256(data).hexdigest() |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:80 | version |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:21 | models.VersionsRow.model_validate_json(cached) |
| backend/src/kotorelay/operations/documents/submit_version/generated/queries.py:18 | db.query('operations/documents/submit_version/sql/assets_get.sql', {'organization_id': organization_id, 'id': id}, AssetsRow) |
| backend/src/kotorelay/operations/documents/submit_version/generated/queries.py:27 | db.execute('operations/documents/submit_version/sql/documents_update.sql', row.model_dump()) |
| backend/src/kotorelay/operations/documents/submit_version/generated/queries.py:34 | db.query('operations/documents/submit_version/sql/drafts_list.sql', {'organization_id': organization_id}, DraftsRow) |
| backend/src/kotorelay/operations/documents/submit_version/generated/queries.py:43 | db.query('operations/documents/submit_version/sql/ocr_runs_get.sql', {'organization_id': organization_id, 'id': id}, OcrRunsRow) |
| backend/src/kotorelay/operations/documents/submit_version/generated/queries.py:52 | db.execute('operations/documents/submit_version/sql/submissions_insert.sql', row.model_dump()) |
| backend/src/kotorelay/operations/documents/submit_version/generated/queries.py:59 | db.execute('operations/documents/submit_version/sql/versions_insert.sql', row.model_dump()) |
| backend/src/kotorelay/operations/documents/submit_version/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/documents/submit_version/router.py:27 | build_response(f.submit(ctx, str(document_id), data, str(key))) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:20 | db.execute('operations/system/authorization/sql/audit_insert.sql', row.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:25 | db.query('operations/system/authorization/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:34 | db.query('operations/system/authorization/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:43 | db.query('operations/system/authorization/sql/idempotency_get.sql', {'organization_id': organization_id, 'id': id}, IdempotencyRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:52 | db.execute('operations/system/authorization/sql/idempotency_insert.sql', row.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:59 | db.query('operations/system/authorization/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:68 | db.execute('operations/system/authorization/sql/organizations_fence.sql', row.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:75 | db.query('operations/system/authorization/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:84 | db.query('operations/system/authorization/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
