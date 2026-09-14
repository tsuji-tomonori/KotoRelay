<!-- 実装から生成。直接編集しない。入力SHA256: ac3b8a89c10fb6f4c0a9456ea4fb59251414105722d4188a0beaca0d8b493f26 -->

# 正本と索引の不一致を確認 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: 正本と索引の不一致を確認。

**Headers**

該当する入力はありません。

認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


**Path Parameters**

該当する入力はありません。

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
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/reconcile_index/functions.py:12 | ctx.user.operator | 'forbidden' | 403 |
| backend/src/kotorelay/operations/indexing/reconcile_index/router.py:28 | f.has_outdated_chunks(current, doc) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/indexing/reconcile_index/router.py:30 | f.needs_index_repair(doc, current) | then / else の実装分岐 | 制御フロー参照 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| kotorelay.operations.indexing.reconcile_index.generated.queries.chunks_list | chunks | SELECT |
| kotorelay.operations.indexing.reconcile_index.generated.queries.documents_list | documents | SELECT |
| kotorelay.operations.system.authorization.generated.queries.departments_list | departments | SELECT |
| kotorelay.operations.system.authorization.generated.queries.memberships_list | memberships | SELECT |
| kotorelay.operations.system.authorization.generated.queries.organizations_get | organizations | SELECT |
| kotorelay.operations.system.authorization.generated.queries.users_list | users | SELECT |

異常時はDB transactionがrollbackします。内容ハッシュ実体は孤立し得るため、公開認可には使いません。配送失敗はoutboxへ記録します。

## 4. 正常系レスポンス

| Status | 説明 | Media type |
| --- | --- | --- |
| 200 | Successful Response | application/json |

##### `200` Successful Response

型: `array<object>`。定義: `{"items": {"additionalProperties": {"type": "string"}, "type": "object"}, "type": "array", "title": "Response Reconcile Index"}`


**応答項目の取得元**

| 実装箇所 | 返却式（DB行・変換結果・固定値） |
| --- | --- |
| backend/src/kotorelay/operations/indexing/reconcile_index/functions.py:32 | {'document_id': doc.id, 'reason': '旧版または停止済みの断片が残留'} |
| backend/src/kotorelay/operations/indexing/reconcile_index/functions.py:46 | {'document_id': doc.id, 'reason': '最新承認版が未反映'} |
| backend/src/kotorelay/operations/indexing/reconcile_index/functions.py:17 | q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org)) |
| backend/src/kotorelay/operations/indexing/reconcile_index/functions.py:22 | q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org)) |
| backend/src/kotorelay/operations/indexing/reconcile_index/functions.py:51 | any((chunk.version_id != doc.latest_version_id or doc.status != 'active' for chunk in current)) |
| backend/src/kotorelay/operations/indexing/reconcile_index/functions.py:37 | bool(doc.status == 'active' and doc.latest_version_id and (not any((c.version_id == doc.latest_version_id and c.ready for c in current)))) |
| backend/src/kotorelay/operations/indexing/reconcile_index/functions.py:12 | require(ctx.user.operator, 'forbidden', 403) |
| backend/src/kotorelay/operations/indexing/reconcile_index/functions.py:27 | [c for c in chunks if c.document_id == doc.id] |
| backend/src/kotorelay/operations/indexing/reconcile_index/generated/queries.py:41 | db.query('operations/indexing/reconcile_index/sql/001_chunks_list.sql', params.model_dump(), ChunksListRow) |
| backend/src/kotorelay/operations/indexing/reconcile_index/generated/queries.py:75 | db.query('operations/indexing/reconcile_index/sql/002_documents_list.sql', params.model_dump(), DocumentsListRow) |
| backend/src/kotorelay/operations/indexing/reconcile_index/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/indexing/reconcile_index/router.py:32 | build_response(differences) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:63 | db.query('operations/system/authorization/sql/002_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:176 | db.query('operations/system/authorization/sql/006_memberships_list.sql', params.model_dump(), MembershipsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:220 | db.query('operations/system/authorization/sql/008_organizations_get.sql', params.model_dump(), OrganizationsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:248 | db.query('operations/system/authorization/sql/009_users_list.sql', params.model_dump(), UsersListRow) |
