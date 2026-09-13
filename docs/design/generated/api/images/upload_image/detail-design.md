<!-- 実装から生成。直接編集しない。入力SHA256: 987c18a693c5fa5c9f59f732c65771f1c047c0829e22a5d72b689276aae93c56 -->

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
| backend/src/kotorelay/context.py:41 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:44 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:83 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/context.py:90 | allowed | not_found | 404 |
| backend/src/kotorelay/context.py:54 | q.organizations_fence(self.db, self.organization) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/images/upload_image/functions.py:61 | 0 < len(data) <= max_bytes | 'invalid_image' | 422 |
| backend/src/kotorelay/operations/images/upload_image/functions.py:64 | source.format in {'PNG', 'JPEG'} and source.width * source.height <= max_pixels and (max(source.width, source.height) <= 8000) | 'invalid_image' | 422 |
| backend/src/kotorelay/operations/images/upload_image/functions.py:77 | len(value) <= max_bytes | 'invalid_image' | 422 |
| backend/src/kotorelay/operations/images/upload_image/functions.py:99 | text | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/images/upload_image/functions.py:23 | len(assets) < ctx.settings.max_document_images | 'limit' | 422 |


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
| backend/src/kotorelay/context.py:91 | doc |
| backend/src/kotorelay/context.py:23 | str(uuid4()) |
| backend/src/kotorelay/context.py:19 | datetime.now(UTC) |
| backend/src/kotorelay/operations/images/upload_image/functions.py:78 | (value, image.width, image.height) |
| backend/src/kotorelay/operations/images/upload_image/functions.py:112 | OcrResult(regions=regions, engine='tesseract-jpn-eng-v1', status='ready') |
| backend/src/kotorelay/operations/images/upload_image/functions.py:95 | OcrResult(regions=[], engine='tesseract-jpn-eng-v1', status='failed') |
| backend/src/kotorelay/operations/images/upload_image/functions.py:57 | {'asset': asset, 'ocr_run': run, 'ocr': result} |
| backend/src/kotorelay/operations/images/upload_image/generated/queries.py:14 | db.execute('operations/images/upload_image/sql/assets_insert.sql', row.model_dump()) |
| backend/src/kotorelay/operations/images/upload_image/generated/queries.py:19 | db.query('operations/images/upload_image/sql/assets_list.sql', {'organization_id': organization_id}, AssetsRow) |
| backend/src/kotorelay/operations/images/upload_image/generated/queries.py:28 | db.execute('operations/images/upload_image/sql/ocr_runs_insert.sql', row.model_dump()) |
| backend/src/kotorelay/operations/images/upload_image/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/images/upload_image/router.py:24 | build_response(f.upload(ctx, str(document_id), file.file.read(ctx.settings.max_image_bytes + 1))) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:25 | db.query('operations/system/authorization/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:34 | db.query('operations/system/authorization/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:59 | db.query('operations/system/authorization/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:68 | db.execute('operations/system/authorization/sql/organizations_fence.sql', row.model_dump()) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:75 | db.query('operations/system/authorization/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:84 | db.query('operations/system/authorization/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
