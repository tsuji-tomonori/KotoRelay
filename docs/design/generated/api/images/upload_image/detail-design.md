<!-- 実装から生成。直接編集しない。入力SHA256: ac3b8a89c10fb6f4c0a9456ea4fb59251414105722d4188a0beaca0d8b493f26 -->

# 画像を添付して位置付きOCRを実行 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: 画像を添付して位置付きOCRを実行。

**Headers**

該当する入力はありません。

認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


**Path Parameters**

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| document_id | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "uuid", "title": "Document Id"} |


**Query Parameters**

該当する入力はありません。

**Data**

媒体: `multipart/form-data`

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| file | string | 必須 | 型定義に説明なし | {"contentMediaType": "application/octet-stream"} |


## 2. 正常系前提

認証・認可と型制約を満たすこと。以下は実装の検査条件と制御分岐です。条件の成立を一律に正常系とは扱いません。

| 実装箇所 | 検査条件 | 不成立時／分岐 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:45 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:52 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:110 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/context.py:117 | allowed | not_found | 404 |
| backend/src/kotorelay/context.py:67 | q.organizations_fence(self.db, q.OrganizationsFenceParams.model_validate(self.organization, from_attributes=True)) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/images/upload_image/functions.py:100 | len(assets) < ctx.settings.max_document_images | 'limit' | 422 |
| backend/src/kotorelay/operations/images/upload_image/functions.py:26 | 0 < len(data) <= max_bytes | 'invalid_image' | 422 |
| backend/src/kotorelay/operations/images/upload_image/functions.py:29 | source.format in {'PNG', 'JPEG'} and source.width * source.height <= max_pixels and (max(source.width, source.height) <= 8000) | 'invalid_image' | 422 |
| backend/src/kotorelay/operations/images/upload_image/functions.py:42 | len(value) <= max_bytes | 'invalid_image' | 422 |
| backend/src/kotorelay/operations/images/upload_image/functions.py:68 | has_recognized_text(text) | then / else の実装分岐 | 制御フロー参照 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| kotorelay.operations.images.upload_image.generated.queries.assets_insert | assets | INSERT |
| kotorelay.operations.images.upload_image.generated.queries.assets_list | assets | SELECT |
| kotorelay.operations.images.upload_image.generated.queries.ocr_runs_insert | ocr_runs | INSERT |
| kotorelay.operations.system.authorization.generated.queries.departments_list | departments | SELECT |
| kotorelay.operations.system.authorization.generated.queries.documents_get | documents | SELECT |
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

型: `object`。定義: `{"type": "object", "additionalProperties": true, "title": "Response Upload Image"}`


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
| backend/src/kotorelay/context.py:118 | doc |
| backend/src/kotorelay/context.py:24 | str(uuid4()) |
| backend/src/kotorelay/context.py:20 | datetime.now(UTC) |
| backend/src/kotorelay/operational_logging.py:150 | OperationalLogContext(request_id=REQUEST_ID.get(), exception_type=type(error).__name__, status=None, code=(error.code if isinstance(error, Problem) else 'external_failure') if message_id == MessageId.INDEX_FAILED else None, message=CATALOG[message_id].response) |
| backend/src/kotorelay/operations/images/upload_image/functions.py:133 | q.assets_insert(ctx.db, q.AssetsInsertParams.model_validate(asset, from_attributes=True)) |
| backend/src/kotorelay/operations/images/upload_image/functions.py:117 | models.AssetsRow(id=new_id(), organization_id=ctx.org, document_id=doc.id, object_key=key, sha256=key, media_type='image/png', width=width, height=height, size=len(value), created_at=now()) |
| backend/src/kotorelay/operations/images/upload_image/functions.py:149 | models.OcrRunsRow(id=new_id(), organization_id=ctx.org, document_id=doc.id, asset_id=asset.id, result_key=result_key, result_hash=result_key, engine=result.engine, status=result.status, confirmed=False, created_at=now()) |
| backend/src/kotorelay/operations/images/upload_image/functions.py:179 | {'asset': asset, 'ocr_run': run, 'ocr': result} |
| backend/src/kotorelay/operations/images/upload_image/functions.py:172 | ctx.fence() |
| backend/src/kotorelay/operations/images/upload_image/functions.py:86 | ctx.document(str(document_id), 'author') |
| backend/src/kotorelay/operations/images/upload_image/functions.py:100 | require(len(assets) < ctx.settings.max_document_images, 'limit', 422) |
| backend/src/kotorelay/operations/images/upload_image/functions.py:184 | bool(text) |
| backend/src/kotorelay/operations/images/upload_image/functions.py:43 | (value, image.width, image.height) |
| backend/src/kotorelay/operations/images/upload_image/functions.py:165 | q.ocr_runs_insert(ctx.db, q.OcrRunsInsertParams.model_validate(run, from_attributes=True)) |
| backend/src/kotorelay/operations/images/upload_image/functions.py:105 | ctx.objects.put(value, 'image/png') |
| backend/src/kotorelay/operations/images/upload_image/functions.py:138 | ctx.objects.put(result.model_dump_json().encode(), 'application/json') |
| backend/src/kotorelay/operations/images/upload_image/functions.py:81 | OcrResult(regions=regions, engine='tesseract-jpn-eng-v1', status='ready') |
| backend/src/kotorelay/operations/images/upload_image/functions.py:64 | OcrResult(regions=[], engine='tesseract-jpn-eng-v1', status='failed') |
| backend/src/kotorelay/operations/images/upload_image/functions.py:91 | [a for a in q.assets_list(ctx.db, q.AssetsListParams(organization_id=ctx.org)) if a.document_id == doc.id] |
| backend/src/kotorelay/operations/images/upload_image/generated/queries.py:33 | db.execute('operations/images/upload_image/sql/001_assets_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/images/upload_image/generated/queries.py:63 | db.query('operations/images/upload_image/sql/002_assets_list.sql', params.model_dump(), AssetsListRow) |
| backend/src/kotorelay/operations/images/upload_image/generated/queries.py:86 | db.execute('operations/images/upload_image/sql/003_ocr_runs_insert.sql', params.model_dump()) |
| backend/src/kotorelay/operations/images/upload_image/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/images/upload_image/router.py:42 | build_response(f.build_upload_image(asset, run, result)) |
| backend/src/kotorelay/operations/system/authorization/functions.py:6 | operation == 'read' |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:63 | db.query('operations/system/authorization/sql/002_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:98 | db.query('operations/system/authorization/sql/003_documents_get.sql', params.model_dump(), DocumentsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:176 | db.query('operations/system/authorization/sql/006_memberships_list.sql', params.model_dump(), MembershipsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:194 | db.execute('operations/system/authorization/sql/007_organizations_fence.sql', params.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:220 | db.query('operations/system/authorization/sql/008_organizations_get.sql', params.model_dump(), OrganizationsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:248 | db.query('operations/system/authorization/sql/009_users_list.sql', params.model_dump(), UsersListRow) |
