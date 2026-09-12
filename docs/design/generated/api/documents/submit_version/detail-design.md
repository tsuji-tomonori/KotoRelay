<!-- 実装から生成。直接編集しない。入力SHA256: 31de213f242d3d7bf0d4f5957d4ef327aaacb2267a973d8e0adce1f1531ac7e1 -->

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
| backend/src/kotorelay/context.py:40 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:43 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:82 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/context.py:89 | allowed | not_found | 404 |
| backend/src/kotorelay/context.py:53 | q.organizations_fence(self.db, self.organization) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/context.py:129 | not rows | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:132 | record.operation == operation and record.request_hash == digest(request.encode()) | 'idempotency_conflict' | 409 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/documents/functions.py:200 | cached | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/documents/functions.py:203 | row.revision == data.revision | 'conflict' | 409 |
| backend/src/kotorelay/operations/documents/functions.py:209 | ocr.confirmed and ocr.status == 'ready' | 'ocr_unconfirmed' | 409 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| assets_get | assets | SELECT |
| audit_insert | audit | INSERT |
| departments_list | departments | SELECT |
| documents_get | documents | SELECT |
| documents_update | documents | UPDATE |
| drafts_list | drafts | SELECT |
| idempotency_get | idempotency | SELECT |
| idempotency_insert | idempotency | INSERT |
| memberships_list | memberships | SELECT |
| ocr_runs_get | ocr_runs | SELECT |
| organizations_fence | organizations | UPDATE |
| organizations_get | organizations | SELECT |
| submissions_insert | submissions | INSERT |
| users_list | users | SELECT |
| versions_insert | versions | INSERT |

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
| backend/src/kotorelay/context.py:90 | doc |
| backend/src/kotorelay/context.py:137 | record.response |
| backend/src/kotorelay/context.py:130 | None |
| backend/src/kotorelay/context.py:22 | str(uuid4()) |
| backend/src/kotorelay/context.py:18 | datetime.now(UTC) |
| backend/src/kotorelay/context.py:26 | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| backend/src/kotorelay/generated/queries.py:553 | db.query('operations/images/sql/assets_get.sql', {'organization_id': organization_id, 'id': id}, AssetsRow) |
| backend/src/kotorelay/generated/queries.py:734 | db.execute('operations/system/sql/audit_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:437 | db.query('operations/groups/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/generated/queries.py:331 | db.query('operations/documents/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/generated/queries.py:354 | db.execute('operations/documents/sql/documents_update.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:380 | db.query('operations/documents/sql/drafts_list.sql', {'organization_id': organization_id}, DraftsRow) |
| backend/src/kotorelay/generated/queries.py:746 | db.query('operations/system/sql/idempotency_get.sql', {'organization_id': organization_id, 'id': id}, IdempotencyRow) |
| backend/src/kotorelay/generated/queries.py:755 | db.execute('operations/system/sql/idempotency_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:473 | db.query('operations/groups/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/generated/queries.py:581 | db.query('operations/images/sql/ocr_runs_get.sql', {'organization_id': organization_id, 'id': id}, OcrRunsRow) |
| backend/src/kotorelay/generated/queries.py:487 | db.execute('operations/identity/sql/organizations_fence.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:492 | db.query('operations/identity/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/generated/queries.py:706 | db.execute('operations/reviews/sql/submissions_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:534 | db.query('operations/identity/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
| backend/src/kotorelay/generated/queries.py:409 | db.execute('operations/documents/sql/versions_insert.sql', row.model_dump()) |
| backend/src/kotorelay/objects.py:17 | hashlib.sha256(data).hexdigest() |
| backend/src/kotorelay/operations/documents/functions.py:260 | version |
| backend/src/kotorelay/operations/documents/functions.py:201 | q.VersionsRow.model_validate_json(cached) |
| backend/src/kotorelay/operations/documents/router.py:56 | f.submit(ctx, str(document_id), data, str(key)) |
