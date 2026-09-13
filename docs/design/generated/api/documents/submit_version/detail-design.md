<!-- 実装から生成。直接編集しない。入力SHA256: 1c655589065a087f66d0ae05a6e0b777b889337ba2d8cca7542a2988c7248164 -->

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
| backend/src/kotorelay/context.py:43 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:50 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:103 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/context.py:110 | allowed | not_found | 404 |
| backend/src/kotorelay/context.py:64 | q.organizations_fence(self.db, q.OrganizationsFenceParams.model_validate(self.organization, from_attributes=True)) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/context.py:153 | not rows | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:156 | record.operation == operation and record.request_hash == digest(request.encode()) | 'idempotency_conflict' | 409 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:62 | ocr.confirmed and ocr.status == 'ready' | 'ocr_unconfirmed' | 409 |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:41 | row.revision == data.revision | 'conflict' | 409 |
| backend/src/kotorelay/operations/documents/submit_version/router.py:33 | cached | then / else の実装分岐 | 制御フロー参照 |


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
| backend/src/kotorelay/context.py:111 | doc |
| backend/src/kotorelay/context.py:161 | record.response |
| backend/src/kotorelay/context.py:154 | None |
| backend/src/kotorelay/context.py:23 | str(uuid4()) |
| backend/src/kotorelay/context.py:19 | datetime.now(UTC) |
| backend/src/kotorelay/context.py:27 | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| backend/src/kotorelay/objects.py:17 | hashlib.sha256(data).hexdigest() |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:48 | q.assets_get(ctx.db, q.AssetsGetParams(organization_id=ctx.org, id=placement.asset_id)) |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:171 | ManifestImage(placement=placement, image_hash=image_hash, ocr_hash=ocr_hash) |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:31 | models.VersionsRow.model_validate_json(cached) |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:84 | models.VersionsRow(id=new_id(), organization_id=ctx.org, document_id=doc.id, number=doc.next_version, title=doc.title, body_key=row.body_key, body_hash=row.body_hash, manifest=manifest, manifest_hash=digest(manifest.encode()), created_by=ctx.user.id, created_at=now()) |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:161 | ctx.fence() |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:21 | ctx.document(str(document_id), 'author') |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:130 | q.documents_update(ctx.db, q.DocumentsUpdateParams.model_validate(doc.model_copy(update={'next_version': doc.next_version + 1, 'revision': doc.revision + 1, 'updated_at': now()}), from_attributes=True)) |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:36 | q.drafts_list(ctx.db, q.DraftsListParams(organization_id=ctx.org)) |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:26 | ctx.idempotent_result(str(key), 'submit', request) |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:55 | q.ocr_runs_get(ctx.db, q.OcrRunsGetParams(organization_id=ctx.org, id=placement.ocr_run_id)) |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:166 | [Placement.model_validate(value) for value in json.loads(row.placements)] |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:149 | ctx.audit('submit', doc.id, version.id, 'draft', 'pending') |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:156 | ctx.remember(str(key), 'submit', request, version.model_dump_json()) |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:62 | require(ocr.confirmed and ocr.status == 'ready', 'ocr_unconfirmed', 409) |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:176 | Manifest(body_hash=body_hash, images=images).model_dump_json() |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:110 | q.submissions_insert(ctx.db, q.SubmissionsInsertParams(id=new_id(), organization_id=ctx.org, document_id=doc.id, version_id=version.id, requested_by=ctx.user.id, status='pending', manifest_hash=version.manifest_hash, decided_by=None, reason='', created_at=now(), decided_at=None)) |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:41 | require(row.revision == data.revision, 'conflict', 409) |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:77 | ctx.objects.get(row.body_key, row.body_hash) |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:67 | ctx.objects.get(asset.object_key, asset.sha256) |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:72 | ctx.objects.get(ocr.result_key, ocr.result_hash) |
| backend/src/kotorelay/operations/documents/submit_version/functions.py:101 | q.versions_insert(ctx.db, q.VersionsInsertParams.model_validate(version, from_attributes=True)) |
| backend/src/kotorelay/operations/documents/submit_version/generated/queries.py:43 | db.query('operations/documents/submit_version/sql/001_assets_get.sql', params.model_dump(), AssetsGetRow) |
| backend/src/kotorelay/operations/documents/submit_version/generated/queries.py:70 | db.execute('operations/documents/submit_version/sql/002_documents_update.sql', params.model_dump()) |
| backend/src/kotorelay/operations/documents/submit_version/generated/queries.py:98 | db.query('operations/documents/submit_version/sql/003_drafts_list.sql', params.model_dump(), DraftsListRow) |
| backend/src/kotorelay/operations/documents/submit_version/generated/queries.py:131 | db.query('operations/documents/submit_version/sql/004_ocr_runs_get.sql', params.model_dump(), OcrRunsGetRow) |
| backend/src/kotorelay/operations/documents/submit_version/generated/queries.py:157 | db.execute('operations/documents/submit_version/sql/005_submissions_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/documents/submit_version/generated/queries.py:181 | db.execute('operations/documents/submit_version/sql/006_versions_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/documents/submit_version/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/documents/submit_version/router.py:54 | build_response(version) |
| backend/src/kotorelay/operations/documents/submit_version/router.py:34 | build_response(f.build_submit_version(cached)) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:39 | db.execute('operations/system/authorization/sql/001_audit_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:63 | db.query('operations/system/authorization/sql/002_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:98 | db.query('operations/system/authorization/sql/003_documents_get.sql', params.model_dump(), DocumentsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:127 | db.query('operations/system/authorization/sql/004_idempotency_get.sql', params.model_dump(), IdempotencyGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:148 | db.execute('operations/system/authorization/sql/005_idempotency_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:176 | db.query('operations/system/authorization/sql/006_memberships_list.sql', params.model_dump(), MembershipsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:194 | db.execute('operations/system/authorization/sql/007_organizations_fence.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:220 | db.query('operations/system/authorization/sql/008_organizations_get.sql', params.model_dump(), OrganizationsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:248 | db.query('operations/system/authorization/sql/009_users_list.sql', params.model_dump(), UsersListRow) |
