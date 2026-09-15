<!-- 実装から生成。直接編集しない。入力SHA256: 065f3a0aaa159ee25b4b54797ae13bebd5e0deb08cdd00f2becc4afbe26e1319 -->

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
| backend/src/kotorelay/context.py:45 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:52 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:67 | q.organizations_fence(self.db, q.OrganizationsFenceParams.model_validate(self.organization, from_attributes=True)) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:474 | row.document_id == document_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:476 | row.document_id in live | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:139 | len(parts) <= 300 | 'limit' | 422 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:378 | job.attempts < 5 | 'limit' | 429 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:373 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:363 | ctx.user.operator | 'forbidden' | 403 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:37 | buffer.strip() | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:25 | line.startswith('#') or len(buffer) + len(line) > 1200 | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:26 | buffer.strip() | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:29 | line.startswith('#') | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:33 | len(buffer) + len(part) > 1200 and buffer.strip() | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/functions.py:221 | len(actual) == len(parts) and engine.verify([c.id for c in actual]) | 'integrity' | 503 |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:20 | f.is_obsolete_version(doc, job) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:26 | f.has_more_stale_chunks(stale) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:28 | f.is_inactive_document(doc) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:46 | f.is_existing_chunk(previous, chunk) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:104 | f.is_finished_job(job) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:61 | f.is_restored_document(doc) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:63 | f.is_within_retention(ctx, job) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:81 | f.has_more_target_chunks(target_chunks) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:86 | f.has_more_target_ocr(target_runs) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:89 | f.is_target_asset(asset, doc) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:92 | f.is_target_draft(draft, doc) | then / else の実装分岐 | 制御フロー参照 |


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
| backend/src/kotorelay/context.py:20 | datetime.now(UTC) |
| backend/src/kotorelay/context.py:28 | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| backend/src/kotorelay/operational_logging.py:150 | OperationalLogContext(request_id=REQUEST_ID.get(), exception_type=type(error).__name__, status=None, code=(error.code if isinstance(error, Problem) else 'external_failure') if message_id == MessageId.INDEX_FAILED else None, message=CATALOG[message_id].response) |
| backend/src/kotorelay/operations/indexing/retry_job/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/indexing/retry_job/router.py:27 | build_response(process(ctx, rt.engine, str(job_id))) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:285 | q.answers_list(ctx.db, q.AnswersListParams(organization_id=ctx.org)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:348 | q.assets_delete(ctx.db, q.AssetsDeleteParams(organization_id=ctx.org, id=asset.id)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:109 | q.assets_get(ctx.db, q.AssetsGetParams(organization_id=ctx.org, id=image.placement.asset_id)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:265 | q.assets_list(ctx.db, q.AssetsListParams(organization_id=ctx.org)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:168 | models.ChunksRow(id=stable_id(version.id + str(number)), organization_id=ctx.org, document_id=doc.id, version_id=version.id, body_key=key, sha256=key, heading=heading, placements=placements, manifest_hash=version.manifest_hash, ready=False) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:92 | Manifest.model_validate_json(version.manifest) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:134 | OcrResult.model_validate_json(ctx.objects.get(run.result_key, image.ocr_hash)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:388 | job.model_copy(update={'status': status, 'attempts': job.attempts if status in {'retained', 'pending'} else job.attempts + 1, 'error_code': ''}) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:399 | job.model_copy(update={'status': 'failed', 'attempts': job.attempts + 1, 'error_code': exc.code}) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:406 | job.model_copy(update={'status': 'failed', 'attempts': job.attempts + 1, 'error_code': 'external_failure'}) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:420 | ctx.fence() |
| backend/src/kotorelay/operations/indexing/shared/functions.py:72 | q.chunks_delete(ctx.db, q.ChunksDeleteParams(organization_id=ctx.org, id=stale_chunk.id)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:316 | q.chunks_delete(ctx.db, q.ChunksDeleteParams(organization_id=ctx.org, id=chunk.id)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:205 | q.chunks_insert(ctx.db, q.ChunksInsertParams.model_validate(chunk, from_attributes=True)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:260 | q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:200 | q.chunks_update(ctx.db, q.ChunksUpdateParams.model_validate(chunk, from_attributes=True)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:233 | q.chunks_update(ctx.db, q.ChunksUpdateParams.model_validate(current.model_copy(update={'ready': True}), from_attributes=True)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:290 | {d.id for d in q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org)) if d.status != 'deleted'} |
| backend/src/kotorelay/operations/indexing/shared/functions.py:485 | (keys, protected) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:97 | ctx.objects.get(version.body_key, version.body_hash).decode() |
| backend/src/kotorelay/operations/indexing/shared/functions.py:67 | engine.delete([c.id for c in stale[:100]]) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:299 | ctx.objects.delete(key) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:311 | engine.delete([c.id for c in target_chunks]) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:44 | q.documents_get(ctx.db, q.DocumentsGetParams(organization_id=ctx.org, id=job.document_id)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:243 | q.documents_get(ctx.db, q.DocumentsGetParams(organization_id=ctx.org, id=job.document_id)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:358 | q.drafts_delete(ctx.db, q.DraftsDeleteParams(organization_id=ctx.org, id=draft.id)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:275 | q.drafts_list(ctx.db, q.DraftsListParams(organization_id=ctx.org)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:139 | require(len(parts) <= 300, 'limit', 422) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:378 | require(job.attempts < 5, 'limit', 429) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:77 | bool(len(stale) > 100) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:321 | bool(len(target_chunks) > 100) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:338 | bool(len(target_runs) > 100) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:430 | [(image.placement.heading or heading, text, json.dumps([image.placement.id])) for heading, text in split_chunks(text or '添付画像')] |
| backend/src/kotorelay/operations/indexing/shared/functions.py:190 | engine.index(chunk.id, text, doc.id, version.id) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:195 | bool(chunk.id in previous) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:383 | bool(job.status in {'done', 'obsolete'}) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:82 | bool(doc.status != 'active') |
| backend/src/kotorelay/operations/indexing/shared/functions.py:51 | bool(doc.latest_version_id != job.version_id or not job.version_id) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:438 | job.kind == 'purge' |
| backend/src/kotorelay/operations/indexing/shared/functions.py:250 | bool(doc.status != 'deleted') |
| backend/src/kotorelay/operations/indexing/shared/functions.py:343 | bool(asset.document_id == doc.id) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:353 | bool(draft.document_id == doc.id) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:255 | bool((now() - job.created_at).total_seconds() < ctx.settings.retention_days * 86400) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:146 | {c.id: c for c in q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org)) if c.version_id == version.id} |
| backend/src/kotorelay/operations/indexing/shared/functions.py:333 | q.ocr_runs_delete(ctx.db, q.OcrRunsDeleteParams(organization_id=ctx.org, id=run.id)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:118 | q.ocr_runs_get(ctx.db, q.OcrRunsGetParams(organization_id=ctx.org, id=image.placement.ocr_run_id)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:270 | q.ocr_runs_list(ctx.db, q.OcrRunsListParams(organization_id=ctx.org)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:368 | q.outbox_get(ctx.db, q.OutboxGetParams(organization_id=ctx.org, id=job_id)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:413 | q.outbox_update(ctx.db, q.OutboxUpdateParams.model_validate(updated, from_attributes=True)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:155 | ctx.objects.put(text.encode(), 'text/plain') |
| backend/src/kotorelay/operations/indexing/shared/functions.py:373 | require(bool(rows)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:363 | require(ctx.user.operator, 'forbidden', 403) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:210 | [c for c in q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org)) if c.version_id == version.id] |
| backend/src/kotorelay/operations/indexing/shared/functions.py:102 | [(heading, text, '[]') for heading, text in split_chunks(body)] |
| backend/src/kotorelay/operations/indexing/shared/functions.py:58 | [c for c in q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org)) if c.document_id == doc.id and (doc.status != 'active' or c.version_id != job.version_id)] |
| backend/src/kotorelay/operations/indexing/shared/functions.py:306 | [c for c in chunks if c.document_id == doc.id] |
| backend/src/kotorelay/operations/indexing/shared/functions.py:328 | [r for r in runs if r.document_id == doc.id] |
| backend/src/kotorelay/operations/indexing/shared/functions.py:39 | chunks |
| backend/src/kotorelay/operations/indexing/shared/functions.py:221 | require(len(actual) == len(parts) and engine.verify([c.id for c in actual]), 'integrity', 503) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:87 | q.versions_get(ctx.db, q.VersionsGetParams(organization_id=ctx.org, id=version_id)) |
| backend/src/kotorelay/operations/indexing/shared/functions.py:280 | q.versions_list(ctx.db, q.VersionsListParams(organization_id=ctx.org)) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:48 | db.query('operations/indexing/shared/sql/001_answers_list.sql', params.model_dump(), AnswersListRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:63 | db.execute('operations/indexing/shared/sql/002_assets_delete.sql', params.model_dump()) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:92 | db.query('operations/indexing/shared/sql/003_assets_get.sql', params.model_dump(), AssetsGetRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:122 | db.query('operations/indexing/shared/sql/004_assets_list.sql', params.model_dump(), AssetsListRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:137 | db.execute('operations/indexing/shared/sql/005_chunks_delete.sql', params.model_dump()) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:158 | db.execute('operations/indexing/shared/sql/006_chunks_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:186 | db.query('operations/indexing/shared/sql/007_chunks_list.sql', params.model_dump(), ChunksListRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:209 | db.execute('operations/indexing/shared/sql/008_chunks_update.sql', params.model_dump()) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:240 | db.query('operations/indexing/shared/sql/009_documents_get.sql', params.model_dump(), DocumentsGetRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:272 | db.query('operations/indexing/shared/sql/010_documents_list.sql', params.model_dump(), DocumentsListRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:289 | db.execute('operations/indexing/shared/sql/011_drafts_delete.sql', params.model_dump()) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:315 | db.query('operations/indexing/shared/sql/012_drafts_list.sql', params.model_dump(), DraftsListRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:330 | db.execute('operations/indexing/shared/sql/013_ocr_runs_delete.sql', params.model_dump()) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:359 | db.query('operations/indexing/shared/sql/014_ocr_runs_get.sql', params.model_dump(), OcrRunsGetRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:389 | db.query('operations/indexing/shared/sql/015_ocr_runs_list.sql', params.model_dump(), OcrRunsListRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:419 | db.query('operations/indexing/shared/sql/016_outbox_get.sql', params.model_dump(), OutboxGetRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:441 | db.execute('operations/indexing/shared/sql/017_outbox_update.sql', params.model_dump()) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:471 | db.query('operations/indexing/shared/sql/018_versions_get.sql', params.model_dump(), VersionsGetRow) |
| backend/src/kotorelay/operations/indexing/shared/generated/queries.py:502 | db.query('operations/indexing/shared/sql/019_versions_list.sql', params.model_dump(), VersionsListRow) |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:55 | 'done' |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:21 | 'obsolete' |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:27 | 'pending' |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:29 | 'done' |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:121 | updated |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:105 | job |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:94 | 'done' |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:62 | 'obsolete' |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:64 | 'retained' |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:82 | 'pending' |
| backend/src/kotorelay/operations/indexing/shared/workflow.py:87 | 'pending' |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:63 | db.query('operations/system/authorization/sql/002_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:176 | db.query('operations/system/authorization/sql/006_memberships_list.sql', params.model_dump(), MembershipsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:194 | db.execute('operations/system/authorization/sql/007_organizations_fence.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:220 | db.query('operations/system/authorization/sql/008_organizations_get.sql', params.model_dump(), OrganizationsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:248 | db.query('operations/system/authorization/sql/009_users_list.sql', params.model_dump(), UsersListRow) |
