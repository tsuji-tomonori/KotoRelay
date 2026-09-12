<!-- 実装から生成。直接編集しない。入力SHA256: 4c18ae62a9b9de513581947abfc60f1ec45b9f631019a142a812724b4695a84b -->

# 競合を検出して下書きを保存 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: 競合を検出して下書きを保存。

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

媒体: `application/json`

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| title | string | 必須 | 型定義に説明なし | {"maxLength": 200, "minLength": 1} |
| body | string | 必須 | 型定義に説明なし | {"maxLength": 100000} |
| revision | integer | 必須 | 型定義に説明なし | {"minimum": 1.0} |
| placements | array<Placement> | 任意 | 型定義に説明なし | {"maxItems": 10} |
| placements[].id | string | 必須 | 型定義に説明なし | {"pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"} |
| placements[].asset_id | string | 必須 | 型定義に説明なし | {"pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"} |
| placements[].ocr_run_id | string | 必須 | 型定義に説明なし | {"pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"} |
| placements[].offset | integer | 必須 | 型定義に説明なし | {"maximum": 100000.0, "minimum": 0.0} |
| placements[].heading | string | 任意 | 型定義に説明なし | {"maxLength": 200, "default": ""} |
| placements[].alt_text | string | 任意 | 型定義に説明なし | {"maxLength": 1000, "default": ""} |
| placements[].caption | string | 任意 | 型定義に説明なし | {"maxLength": 2000, "default": ""} |


## 2. 正常系前提

認証・認可と型制約を満たすこと。以下は実装の検査条件と制御分岐です。条件の成立を一律に正常系とは扱いません。

| 実装箇所 | 検査条件 | 不成立時／分岐 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:40 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:43 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:82 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/context.py:89 | allowed | not_found | 404 |
| backend/src/kotorelay/context.py:53 | q.organizations_fence(self.db, self.organization) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/documents/functions.py:171 | row.revision == data.revision | 'conflict' | 409 |
| backend/src/kotorelay/operations/documents/functions.py:153 | len({p.id for p in data.placements}) == len(data.placements) | 'invalid_placement' | 422 |
| backend/src/kotorelay/operations/documents/functions.py:157 | bool(assets) and bool(runs) | 'invalid_placement' | 422 |
| backend/src/kotorelay/operations/documents/functions.py:158 | assets[0].document_id == doc.id and runs[0].asset_id == assets[0].id and (runs[0].document_id == doc.id) and (placement.offset <= len(data.body)) | 'invalid_placement' | 422 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| assets_get | assets | SELECT |
| departments_list | departments | SELECT |
| documents_get | documents | SELECT |
| documents_update | documents | UPDATE |
| drafts_list | drafts | SELECT |
| drafts_update | drafts | UPDATE |
| memberships_list | memberships | SELECT |
| ocr_runs_get | ocr_runs | SELECT |
| organizations_fence | organizations | UPDATE |
| organizations_get | organizations | SELECT |
| users_list | users | SELECT |

異常時はDB transactionがrollbackします。内容ハッシュ実体は孤立し得るため、公開認可には使いません。配送失敗はoutboxへ記録します。

## 4. 正常系レスポンス

| Status | 説明 | Media type |
| --- | --- | --- |
| 200 | Successful Response | application/json |
| 422 | Validation Error | application/json |

##### `200` Successful Response

型: `object`。定義: `{"type": "object", "additionalProperties": true, "title": "Response Save Draft"}`


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
| backend/src/kotorelay/context.py:18 | datetime.now(UTC) |
| backend/src/kotorelay/generated/queries.py:553 | db.query('operations/images/sql/assets_get.sql', {'organization_id': organization_id, 'id': id}, AssetsRow) |
| backend/src/kotorelay/generated/queries.py:437 | db.query('operations/groups/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/generated/queries.py:331 | db.query('operations/documents/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/generated/queries.py:354 | db.execute('operations/documents/sql/documents_update.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:380 | db.query('operations/documents/sql/drafts_list.sql', {'organization_id': organization_id}, DraftsRow) |
| backend/src/kotorelay/generated/queries.py:387 | db.execute('operations/documents/sql/drafts_update.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:473 | db.query('operations/groups/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/generated/queries.py:581 | db.query('operations/images/sql/ocr_runs_get.sql', {'organization_id': organization_id, 'id': id}, OcrRunsRow) |
| backend/src/kotorelay/generated/queries.py:487 | db.execute('operations/identity/sql/organizations_fence.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:492 | db.query('operations/identity/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/generated/queries.py:534 | db.query('operations/identity/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
| backend/src/kotorelay/operations/documents/functions.py:144 | {'document': doc, 'body': ctx.objects.get(row.body_key, row.body_hash).decode(), 'revision': row.revision, 'placements': json.loads(row.placements)} |
| backend/src/kotorelay/operations/documents/functions.py:193 | draft(ctx, doc.id) |
| backend/src/kotorelay/operations/documents/router.py:46 | f.save(ctx, str(document_id), data) |
