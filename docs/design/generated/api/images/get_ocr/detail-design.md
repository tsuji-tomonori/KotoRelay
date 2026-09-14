<!-- 実装から生成。直接編集しない。入力SHA256: dc958b6e6841a9f29856eb932e8271e37a6d4416a3266624301c411c89949f81 -->

# 認可されたOCR領域を取得 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: 認可されたOCR領域を取得。

**Headers**

該当する入力はありません。

認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


**Path Parameters**

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| run_id | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "uuid", "title": "Run Id"} |


**Query Parameters**

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| version_id | string &#124; null | 任意 | OpenAPIの型制約に従う | {"anyOf": [{"type": "string", "format": "uuid"}, {"type": "null"}], "title": "Version Id"} |


**Data**

リクエスト本文はありません。

## 2. 正常系前提

認証・認可と型制約を満たすこと。以下は実装の検査条件と制御分岐です。条件の成立を一律に正常系とは扱いません。

| 実装箇所 | 検査条件 | 不成立時／分岐 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:45 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:52 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:95 | doc.status != 'active' or not self.memberships | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:97 | doc.visibility == 'organization' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:99 | self.member(doc.department_id) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:110 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/context.py:117 | allowed | not_found | 404 |
| backend/src/kotorelay/context.py:84 | m.department_id == department_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:125 | not self.permission(doc.department_id, 'draft') | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:123 | bool(rows) and rows[0].document_id == doc.id | not_found | 404 |
| backend/src/kotorelay/context.py:127 | digest(version.manifest.encode()) == version.manifest_hash | 'integrity' | 503 |
| backend/src/kotorelay/context.py:126 | self.can_read(doc) and doc.latest_version_id == version.id | not_found | 404 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/images/get_ocr/functions.py:23 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/operations/images/get_ocr/functions.py:42 | any((i.placement.ocr_run_id == run.id and i.ocr_hash == run.result_hash for i in Manifest.model_validate_json(version.manifest).images)) | not_found | 404 |
| backend/src/kotorelay/operations/images/get_ocr/router.py:34 | f.has_requested_version(version_id) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/images/shared/functions.py:19 | has_no_requested_version(version_id) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/images/shared/functions.py:17 | bool(assets) | not_found | 404 |
| backend/src/kotorelay/operations/images/shared/functions.py:25 | bool(docs) and docs[0].status != 'deleted' | not_found | 404 |
| backend/src/kotorelay/operations/images/shared/functions.py:27 | ctx.can_read(doc) or ctx.permission(doc.department_id, 'draft') | not_found | 404 |
| backend/src/kotorelay/operations/images/shared/functions.py:30 | any((i.placement.asset_id == asset.id and i.image_hash == asset.sha256 for i in manifest.images)) | not_found | 404 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| kotorelay.operations.images.get_ocr.generated.queries.documents_get | documents | SELECT |
| kotorelay.operations.images.get_ocr.generated.queries.ocr_runs_get | ocr_runs | SELECT |
| kotorelay.operations.images.shared.generated.queries.assets_get | assets | SELECT |
| kotorelay.operations.images.shared.generated.queries.documents_get | documents | SELECT |
| kotorelay.operations.system.authorization.generated.queries.departments_list | departments | SELECT |
| kotorelay.operations.system.authorization.generated.queries.documents_get | documents | SELECT |
| kotorelay.operations.system.authorization.generated.queries.memberships_list | memberships | SELECT |
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
| confirmed | boolean | 任意 | 型定義に説明なし | {"default": false} |
| regions | array<Region> | 必須 | 型定義に説明なし | {"maxItems": 1000} |
| regions[].region_id | string &#124; null | 任意 | 型定義に説明なし | {"anyOf": [{"type": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"}, {"type": "null"}]} |
| regions[].source | string | 任意 | 型定義に説明なし | {"enum": ["detected", "human"], "default": "detected"} |
| regions[].text | string | 必須 | 型定義に説明なし | {"maxLength": 5000} |
| regions[].x | number | 必須 | 型定義に説明なし | {"maximum": 1.0, "minimum": 0.0} |
| regions[].y | number | 必須 | 型定義に説明なし | {"maximum": 1.0, "minimum": 0.0} |
| regions[].width | number | 必須 | 型定義に説明なし | {"maximum": 1.0, "minimum": 0.0} |
| regions[].height | number | 必須 | 型定義に説明なし | {"maximum": 1.0, "minimum": 0.0} |
| regions[].confidence | number &#124; null | 任意 | 型定義に説明なし | {"anyOf": [{"type": "number", "maximum": 1.0, "minimum": 0.0}, {"type": "null"}]} |
| regions[].order | integer | 必須 | 型定義に説明なし | {"minimum": 0.0} |
| engine | string | 必須 | 型定義に説明なし | {"maxLength": 100} |
| status | string | 必須 | 型定義に説明なし | {"enum": ["ready", "failed"]} |


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
| backend/src/kotorelay/context.py:101 | doc.visibility == 'selected' and any((self.member(department) for department in json.loads(doc.shared_departments))) |
| backend/src/kotorelay/context.py:96 | False |
| backend/src/kotorelay/context.py:98 | True |
| backend/src/kotorelay/context.py:100 | True |
| backend/src/kotorelay/context.py:118 | doc |
| backend/src/kotorelay/context.py:91 | False |
| backend/src/kotorelay/context.py:85 | {'author': m.can_author, 'review': m.can_review, 'manage': m.leader, 'draft': m.can_author or m.can_review}.get(operation, False) |
| backend/src/kotorelay/context.py:129 | version |
| backend/src/kotorelay/context.py:28 | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| backend/src/kotorelay/objects.py:17 | hashlib.sha256(data).hexdigest() |
| backend/src/kotorelay/operations/images/get_ocr/functions.py:59 | result.model_copy(update={'confirmed': run.confirmed, 'regions': [r.model_copy(update={'region_id': r.region_id or stable_id(run.id + ':' + str(i))}) for i, r in enumerate(result.regions)]}) |
| backend/src/kotorelay/operations/images/get_ocr/functions.py:52 | OcrResult.model_validate_json(ctx.objects.get(run.result_key, run.result_hash)) |
| backend/src/kotorelay/operations/images/get_ocr/functions.py:28 | q.documents_get(ctx.db, q.DocumentsGetParams(organization_id=ctx.org, id=asset.document_id)) |
| backend/src/kotorelay/operations/images/get_ocr/functions.py:72 | bool(version_id) |
| backend/src/kotorelay/operations/images/get_ocr/functions.py:18 | q.ocr_runs_get(ctx.db, q.OcrRunsGetParams(organization_id=ctx.org, id=str(run_id))) |
| backend/src/kotorelay/operations/images/get_ocr/functions.py:23 | require(bool(rows)) |
| backend/src/kotorelay/operations/images/get_ocr/functions.py:42 | require(any((i.placement.ocr_run_id == run.id and i.ocr_hash == run.result_hash for i in Manifest.model_validate_json(version.manifest).images))) |
| backend/src/kotorelay/operations/images/get_ocr/functions.py:37 | ctx.version(doc, str(version_id)) |
| backend/src/kotorelay/operations/images/get_ocr/generated/queries.py:44 | db.query('operations/images/get_ocr/sql/001_documents_get.sql', params.model_dump(), DocumentsGetRow) |
| backend/src/kotorelay/operations/images/get_ocr/generated/queries.py:75 | db.query('operations/images/get_ocr/sql/002_ocr_runs_get.sql', params.model_dump(), OcrRunsGetRow) |
| backend/src/kotorelay/operations/images/get_ocr/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/images/get_ocr/router.py:39 | build_response(f.build_get_ocr(result, run)) |
| backend/src/kotorelay/operations/images/shared/functions.py:36 | asset |
| backend/src/kotorelay/operations/images/shared/functions.py:41 | version_id is None |
| backend/src/kotorelay/operations/images/shared/generated/queries.py:42 | db.query('operations/images/shared/sql/001_assets_get.sql', params.model_dump(), AssetsGetRow) |
| backend/src/kotorelay/operations/images/shared/generated/queries.py:75 | db.query('operations/images/shared/sql/002_documents_get.sql', params.model_dump(), DocumentsGetRow) |
| backend/src/kotorelay/operations/system/authorization/functions.py:6 | operation == 'read' |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:63 | db.query('operations/system/authorization/sql/002_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:98 | db.query('operations/system/authorization/sql/003_documents_get.sql', params.model_dump(), DocumentsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:176 | db.query('operations/system/authorization/sql/006_memberships_list.sql', params.model_dump(), MembershipsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:220 | db.query('operations/system/authorization/sql/008_organizations_get.sql', params.model_dump(), OrganizationsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:248 | db.query('operations/system/authorization/sql/009_users_list.sql', params.model_dump(), UsersListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:280 | db.query('operations/system/authorization/sql/010_versions_get.sql', params.model_dump(), VersionsGetRow) |
