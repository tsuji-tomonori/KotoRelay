<!-- 実装から生成。直接編集しない。入力SHA256: 4c18ae62a9b9de513581947abfc60f1ec45b9f631019a142a812724b4695a84b -->

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
| backend/src/kotorelay/context.py:40 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:43 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:53 | q.organizations_fence(self.db, self.organization) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:40 | doc.latest_version_id != job.version_id or not job.version_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:50 | len(stale) > 100 | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:52 | doc.status != 'active' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:70 | len(parts) <= 300 | 'limit' | 422 |
| backend/src/kotorelay/operations/indexing/functions.py:87 | chunk.id in previous | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:92 | len(actual) == len(parts) and engine.verify([c.id for c in actual]) | 'integrity' | 503 |
| backend/src/kotorelay/operations/indexing/functions.py:170 | job.status in {'done', 'obsolete'} | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:165 | ctx.user.operator | 'forbidden' | 403 |
| backend/src/kotorelay/operations/indexing/functions.py:167 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/operations/indexing/functions.py:169 | job.attempts < 5 | 'limit' | 429 |
| backend/src/kotorelay/operations/indexing/functions.py:101 | doc.status != 'deleted' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:103 | (now() - job.created_at).total_seconds() < ctx.settings.retention_days * 86400 | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:148 | len(target_chunks) > 100 | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:153 | len(target_runs) > 100 | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:156 | asset.document_id == doc.id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:159 | draft.document_id == doc.id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:132 | row.document_id == doc.id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:134 | row.document_id in live | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:33 | buffer.strip() | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:21 | line.startswith('#') or len(buffer) + len(line) > 1200 | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:22 | buffer.strip() | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:25 | line.startswith('#') | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/functions.py:29 | len(buffer) + len(part) > 1200 and buffer.strip() | then / else の実装分岐 | 制御フロー参照 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| answers_list | answers | SELECT |
| assets_delete | assets | DELETE |
| assets_get | assets | SELECT |
| assets_list | assets | SELECT |
| chunks_delete | chunks | DELETE |
| chunks_insert | chunks | INSERT |
| chunks_list | chunks | SELECT |
| chunks_update | chunks | UPDATE |
| departments_list | departments | SELECT |
| documents_get | documents | SELECT |
| documents_list | documents | SELECT |
| drafts_delete | drafts | DELETE |
| drafts_list | drafts | SELECT |
| memberships_list | memberships | SELECT |
| ocr_runs_delete | ocr_runs | DELETE |
| ocr_runs_get | ocr_runs | SELECT |
| ocr_runs_list | ocr_runs | SELECT |
| organizations_fence | organizations | UPDATE |
| organizations_get | organizations | SELECT |
| outbox_get | outbox | SELECT |
| outbox_update | outbox | UPDATE |
| users_list | users | SELECT |
| versions_get | versions | SELECT |
| versions_list | versions | SELECT |

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
| backend/src/kotorelay/context.py:18 | datetime.now(UTC) |
| backend/src/kotorelay/context.py:26 | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| backend/src/kotorelay/generated/queries.py:264 | db.query('operations/chat/sql/answers_list.sql', {'organization_id': organization_id}, AnswersRow) |
| backend/src/kotorelay/generated/queries.py:546 | db.execute('operations/images/sql/assets_delete.sql', {'organization_id': organization_id, 'id': id}) |
| backend/src/kotorelay/generated/queries.py:553 | db.query('operations/images/sql/assets_get.sql', {'organization_id': organization_id, 'id': id}, AssetsRow) |
| backend/src/kotorelay/generated/queries.py:567 | db.query('operations/images/sql/assets_list.sql', {'organization_id': organization_id}, AssetsRow) |
| backend/src/kotorelay/generated/queries.py:602 | db.execute('operations/indexing/sql/chunks_delete.sql', {'organization_id': organization_id, 'id': id}) |
| backend/src/kotorelay/generated/queries.py:618 | db.execute('operations/indexing/sql/chunks_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:623 | db.query('operations/indexing/sql/chunks_list.sql', {'organization_id': organization_id}, ChunksRow) |
| backend/src/kotorelay/generated/queries.py:630 | db.execute('operations/indexing/sql/chunks_update.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:437 | db.query('operations/groups/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/generated/queries.py:331 | db.query('operations/documents/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/generated/queries.py:345 | db.query('operations/documents/sql/documents_list.sql', {'organization_id': organization_id}, DocumentsRow) |
| backend/src/kotorelay/generated/queries.py:359 | db.execute('operations/documents/sql/drafts_delete.sql', {'organization_id': organization_id, 'id': id}) |
| backend/src/kotorelay/generated/queries.py:380 | db.query('operations/documents/sql/drafts_list.sql', {'organization_id': organization_id}, DraftsRow) |
| backend/src/kotorelay/generated/queries.py:473 | db.query('operations/groups/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/generated/queries.py:574 | db.execute('operations/images/sql/ocr_runs_delete.sql', {'organization_id': organization_id, 'id': id}) |
| backend/src/kotorelay/generated/queries.py:581 | db.query('operations/images/sql/ocr_runs_get.sql', {'organization_id': organization_id, 'id': id}, OcrRunsRow) |
| backend/src/kotorelay/generated/queries.py:595 | db.query('operations/images/sql/ocr_runs_list.sql', {'organization_id': organization_id}, OcrRunsRow) |
| backend/src/kotorelay/generated/queries.py:487 | db.execute('operations/identity/sql/organizations_fence.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:492 | db.query('operations/identity/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/generated/queries.py:642 | db.query('operations/indexing/sql/outbox_get.sql', {'organization_id': organization_id, 'id': id}, OutboxRow) |
| backend/src/kotorelay/generated/queries.py:663 | db.execute('operations/indexing/sql/outbox_update.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:534 | db.query('operations/identity/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
| backend/src/kotorelay/generated/queries.py:400 | db.query('operations/documents/sql/versions_get.sql', {'organization_id': organization_id, 'id': id}, VersionsRow) |
| backend/src/kotorelay/generated/queries.py:414 | db.query('operations/documents/sql/versions_list.sql', {'organization_id': organization_id}, VersionsRow) |
| backend/src/kotorelay/operations/indexing/functions.py:96 | 'done' |
| backend/src/kotorelay/operations/indexing/functions.py:41 | 'obsolete' |
| backend/src/kotorelay/operations/indexing/functions.py:51 | 'pending' |
| backend/src/kotorelay/operations/indexing/functions.py:53 | 'done' |
| backend/src/kotorelay/operations/indexing/functions.py:195 | updated |
| backend/src/kotorelay/operations/indexing/functions.py:171 | job |
| backend/src/kotorelay/operations/indexing/functions.py:161 | 'done' |
| backend/src/kotorelay/operations/indexing/functions.py:102 | 'obsolete' |
| backend/src/kotorelay/operations/indexing/functions.py:104 | 'retained' |
| backend/src/kotorelay/operations/indexing/functions.py:149 | 'pending' |
| backend/src/kotorelay/operations/indexing/functions.py:154 | 'pending' |
| backend/src/kotorelay/operations/indexing/functions.py:35 | chunks |
| backend/src/kotorelay/operations/indexing/router.py:21 | f.process(ctx, rt.engine, str(job_id)) |
