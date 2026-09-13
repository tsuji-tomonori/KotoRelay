<!-- 実装から生成。直接編集しない。入力SHA256: 987c18a693c5fa5c9f59f732c65771f1c047c0829e22a5d72b689276aae93c56 -->

# 現在の認可で画像を配信 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: 現在の認可で画像を配信。

**Headers**

該当する入力はありません。

認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


**Path Parameters**

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| asset_id | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "uuid", "title": "Asset Id"} |


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
| backend/src/kotorelay/context.py:41 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:44 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:71 | doc.status != 'active' or not self.memberships | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:73 | doc.visibility == 'organization' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:75 | self.member(doc.department_id) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:83 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/context.py:90 | allowed | not_found | 404 |
| backend/src/kotorelay/context.py:61 | m.department_id == department_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:97 | not self.permission(doc.department_id, 'draft') | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:95 | bool(rows) and rows[0].document_id == doc.id | not_found | 404 |
| backend/src/kotorelay/context.py:99 | digest(version.manifest.encode()) == version.manifest_hash | 'integrity' | 503 |
| backend/src/kotorelay/context.py:98 | self.can_read(doc) and doc.latest_version_id == version.id | not_found | 404 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/images/shared/functions.py:16 | version_id is None | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/images/shared/functions.py:14 | bool(assets) | not_found | 404 |
| backend/src/kotorelay/operations/images/shared/functions.py:20 | bool(docs) and docs[0].status != 'deleted' | not_found | 404 |
| backend/src/kotorelay/operations/images/shared/functions.py:22 | ctx.can_read(doc) or ctx.permission(doc.department_id, 'draft') | not_found | 404 |
| backend/src/kotorelay/operations/images/shared/functions.py:25 | any((i.placement.asset_id == asset.id and i.image_hash == asset.sha256 for i in manifest.images)) | not_found | 404 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
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
| 200 | Successful Response | 本文なし |
| 422 | Validation Error | application/json |

##### `200` Successful Response



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
| backend/src/kotorelay/context.py:77 | doc.visibility == 'selected' and any((self.member(department) for department in json.loads(doc.shared_departments))) |
| backend/src/kotorelay/context.py:72 | False |
| backend/src/kotorelay/context.py:74 | True |
| backend/src/kotorelay/context.py:76 | True |
| backend/src/kotorelay/context.py:91 | doc |
| backend/src/kotorelay/context.py:68 | False |
| backend/src/kotorelay/context.py:62 | {'author': m.can_author, 'review': m.can_review, 'manage': m.leader, 'draft': m.can_author or m.can_review}.get(operation, False) |
| backend/src/kotorelay/context.py:101 | version |
| backend/src/kotorelay/objects.py:17 | hashlib.sha256(data).hexdigest() |
| backend/src/kotorelay/operations/images/get_image/functions.py:11 | ctx.objects.get(asset.object_key, asset.sha256) |
| backend/src/kotorelay/operations/images/get_image/response_builders.py:10 | Response(value, media_type='image/png') |
| backend/src/kotorelay/operations/images/get_image/router.py:25 | build_response(f.image(ctx, str(asset_id), str(version_id) if version_id else None)) |
| backend/src/kotorelay/operations/images/shared/functions.py:31 | asset |
| backend/src/kotorelay/operations/images/shared/generated/queries.py:14 | db.query('operations/images/shared/sql/assets_get.sql', {'organization_id': organization_id, 'id': id}, AssetsRow) |
| backend/src/kotorelay/operations/images/shared/generated/queries.py:23 | db.query('operations/images/shared/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:25 | db.query('operations/system/authorization/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:34 | db.query('operations/system/authorization/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:59 | db.query('operations/system/authorization/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:75 | db.query('operations/system/authorization/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:84 | db.query('operations/system/authorization/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:93 | db.query('operations/system/authorization/sql/versions_get.sql', {'organization_id': organization_id, 'id': id}, VersionsRow) |
