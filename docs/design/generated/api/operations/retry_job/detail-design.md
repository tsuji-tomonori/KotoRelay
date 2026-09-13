<!-- 実装から生成。直接編集しない。入力SHA256: 987c18a693c5fa5c9f59f732c65771f1c047c0829e22a5d72b689276aae93c56 -->

# 反映ジョブを再処理 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: 反映ジョブを再処理。

**Headers**

該当する入力はありません。

認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


**Path Parameters**

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| job_id | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "uuid", "title": "Job Id"} |


**Query Parameters**

該当する入力はありません。

**Data**

リクエスト本文はありません。

## 2. 正常系前提

認証・認可と型制約を満たすこと。以下は実装の検査条件と制御分岐です。条件の成立を一律に正常系とは扱いません。

| 実装箇所 | 検査条件 | 不成立時／分岐 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:41 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:44 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:54 | q.organizations_fence(self.db, self.organization) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:41 | doc.latest_version_id != job.version_id or not job.version_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:51 | len(stale) > 100 | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:53 | doc.status != 'active' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:71 | len(parts) <= 300 | 'limit' | 422 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:88 | chunk.id in previous | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:93 | len(actual) == len(parts) and engine.verify([c.id for c in actual]) | 'integrity' | 503 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:171 | job.status in {'done', 'obsolete'} | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:166 | ctx.user.operator | 'forbidden' | 403 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:168 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:170 | job.attempts < 5 | 'limit' | 429 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:102 | doc.status != 'deleted' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:104 | (now() - job.created_at).total_seconds() < ctx.settings.retention_days * 86400 | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:149 | len(target_chunks) > 100 | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:154 | len(target_runs) > 100 | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:157 | asset.document_id == doc.id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:160 | draft.document_id == doc.id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:133 | row.document_id == doc.id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:135 | row.document_id in live | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:34 | buffer.strip() | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:22 | line.startswith('#') or len(buffer) + len(line) > 1200 | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:23 | buffer.strip() | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:26 | line.startswith('#') | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:30 | len(buffer) + len(part) > 1200 and buffer.strip() | then / else の実装分岐 | 制御フロー参照 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| kotorelay.operations.indexing.shared.generated.queries.answers_list | answers | SELECT |
| kotorelay.operations.indexing.shared.generated.queries.assets_delete | assets | DELETE |
| kotorelay.operations.indexing.shared.generated.queries.assets_get | assets | SELECT |
| kotorelay.operations.indexing.shared.generated.queries.assets_list | assets | SELECT |
| kotorelay.operations.indexing.shared.generated.queries.chunks_delete | chunks | DELETE |
| kotorelay.operations.indexing.shared.generated.queries.chunks_insert | chunks | INSERT |
| kotorelay.operations.indexing.shared.generated.queries.chunks_list | chunks | SELECT |
| kotorelay.operations.indexing.shared.generated.queries.chunks_update | chunks | UPDATE |
| kotorelay.operations.indexing.shared.generated.queries.documents_get | documents | SELECT |
| kotorelay.operations.indexing.shared.generated.queries.documents_list | documents | SELECT |
| kotorelay.operations.indexing.shared.generated.queries.drafts_delete | drafts | DELETE |
| kotorelay.operations.indexing.shared.generated.queries.drafts_list | drafts | SELECT |
| kotorelay.operations.indexing.shared.generated.queries.ocr_runs_delete | ocr_runs | DELETE |
| kotorelay.operations.indexing.shared.generated.queries.ocr_runs_get | ocr_runs | SELECT |
| kotorelay.operations.indexing.shared.generated.queries.ocr_runs_list | ocr_runs | SELECT |
| kotorelay.operations.indexing.shared.generated.queries.outbox_get | outbox | SELECT |
| kotorelay.operations.indexing.shared.generated.queries.outbox_update | outbox | UPDATE |
| kotorelay.operations.indexing.shared.generated.queries.versions_get | versions | SELECT |
| kotorelay.operations.indexing.shared.generated.queries.versions_list | versions | SELECT |
| kotorelay.operations.system.authorization.generated.queries.departments_list | departments | SELECT |
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
| organization_id | string | 必須 | 型定義に説明なし | {} |
| document_id | string | 必須 | 型定義に説明なし | {} |
| version_id | string &#124; null | 必須 | 型定義に説明なし | {"anyOf": [{"type": "string"}, {"type": "null"}]} |
| kind | string | 必須 | 型定義に説明なし | {} |
| status | string | 必須 | 型定義に説明なし | {} |
| attempts | integer | 必須 | 型定義に説明なし | {} |
| error_code | string | 必須 | 型定義に説明なし | {} |
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
| backend/src/kotorelay/context.py:19 | datetime.now(UTC) |
| backend/src/kotorelay/context.py:27 | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| backend/src/kotorelay/operations/indexing/retry_job/functions.py:13 | process(ctx, engine, job_id) |
| backend/src/kotorelay/operations/indexing/retry_job/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/indexing/retry_job/router.py:24 | build_response(f.retry(ctx, rt.engine, str(job_id))) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:97 | 'done' |
| backend/src/kotorelay/operations/indexing/shared/functions.py:42 | 'obsolete' |
| backend/src/kotorelay/operations/indexing/shared/functions.py:52 | 'pending' |
| backend/src/kotorelay/operations/indexing/shared/functions.py:54 | 'done' |
| backend/src/kotorelay/operations/indexing/shared/functions.py:196 | updated |
| backend/src/kotorelay/operations/indexing/shared/functions.py:172 | job |
| backend/src/kotorelay/operations/indexing/shared/functions.py:162 | 'done' |
| backend/src/kotorelay/operations/indexing/shared/functions.py:103 | 'obsolete' |
| backend/src/kotorelay/operations/indexing/shared/functions.py:105 | 'retained' |
| backend/src/kotorelay/operations/indexing/shared/functions.py:150 | 'pending' |
| backend/src/kotorelay/operations/indexing/shared/functions.py:155 | 'pending' |
| backend/src/kotorelay/operations/indexing/shared/functions.py:36 | chunks |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:20 | db.query('operations/indexing/shared/sql/answers_list.sql', {'organization_id': organization_id}, AnswersRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:29 | db.execute('operations/indexing/shared/sql/assets_delete.sql', {'organization_id': organization_id, 'id': id}) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:37 | db.query('operations/indexing/shared/sql/assets_get.sql', {'organization_id': organization_id, 'id': id}, AssetsRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:46 | db.query('operations/indexing/shared/sql/assets_list.sql', {'organization_id': organization_id}, AssetsRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:55 | db.execute('operations/indexing/shared/sql/chunks_delete.sql', {'organization_id': organization_id, 'id': id}) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:63 | db.execute('operations/indexing/shared/sql/chunks_insert.sql', row.model_dump()) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:68 | db.query('operations/indexing/shared/sql/chunks_list.sql', {'organization_id': organization_id}, ChunksRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:77 | db.execute('operations/indexing/shared/sql/chunks_update.sql', row.model_dump()) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:82 | db.query('operations/indexing/shared/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:91 | db.query('operations/indexing/shared/sql/documents_list.sql', {'organization_id': organization_id}, DocumentsRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:100 | db.execute('operations/indexing/shared/sql/drafts_delete.sql', {'organization_id': organization_id, 'id': id}) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:108 | db.query('operations/indexing/shared/sql/drafts_list.sql', {'organization_id': organization_id}, DraftsRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:117 | db.execute('operations/indexing/shared/sql/ocr_runs_delete.sql', {'organization_id': organization_id, 'id': id}) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:125 | db.query('operations/indexing/shared/sql/ocr_runs_get.sql', {'organization_id': organization_id, 'id': id}, OcrRunsRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:134 | db.query('operations/indexing/shared/sql/ocr_runs_list.sql', {'organization_id': organization_id}, OcrRunsRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:143 | db.query('operations/indexing/shared/sql/outbox_get.sql', {'organization_id': organization_id, 'id': id}, OutboxRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:152 | db.execute('operations/indexing/shared/sql/outbox_update.sql', row.model_dump()) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:157 | db.query('operations/indexing/shared/sql/versions_get.sql', {'organization_id': organization_id, 'id': id}, VersionsRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:166 | db.query('operations/indexing/shared/sql/versions_list.sql', {'organization_id': organization_id}, VersionsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:25 | db.query('operations/system/authorization/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:59 | db.query('operations/system/authorization/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:68 | db.execute('operations/system/authorization/sql/organizations_fence.sql', row.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:75 | db.query('operations/system/authorization/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:84 | db.query('operations/system/authorization/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
