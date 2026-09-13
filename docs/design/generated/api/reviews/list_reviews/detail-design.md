<!-- 実装から生成。直接編集しない。入力SHA256: 1c655589065a087f66d0ae05a6e0b777b889337ba2d8cca7542a2988c7248164 -->

# 審査状況を一覧 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: 審査状況を一覧。

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
| backend/src/kotorelay/context.py:43 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:50 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:79 | m.department_id == department_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| kotorelay.operations.reviews.list_reviews.generated.queries.departments_list | departments | SELECT |
| kotorelay.operations.reviews.list_reviews.generated.queries.documents_list | documents | SELECT |
| kotorelay.operations.reviews.list_reviews.generated.queries.submissions_list | submissions | SELECT |
| kotorelay.operations.reviews.list_reviews.generated.queries.users_list | users | SELECT |
| kotorelay.operations.reviews.list_reviews.generated.queries.versions_list | versions | SELECT |
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

型: `array<object>`。定義: `{"items": {"additionalProperties": true, "type": "object"}, "type": "array", "title": "Response List Reviews"}`


**応答項目の取得元**

| 実装箇所 | 返却式（DB行・変換結果・固定値） |
| --- | --- |
| backend/src/kotorelay/context.py:86 | False |
| backend/src/kotorelay/context.py:80 | {'author': m.can_author, 'review': m.can_review, 'manage': m.leader, 'draft': m.can_author or m.can_review}.get(operation, False) |
| backend/src/kotorelay/operations/reviews/list_reviews/functions.py:34 | {d.id: d.name for d in q.departments_list(ctx.db, q.DepartmentsListParams(organization_id=ctx.org))} |
| backend/src/kotorelay/operations/reviews/list_reviews/functions.py:11 | {d.id: d for d in q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org)) if d.status != 'deleted' and (ctx.permission(d.department_id, 'review') or ctx.permission(d.department_id, 'manage'))} |
| backend/src/kotorelay/operations/reviews/list_reviews/functions.py:26 | {u.id: u.display_name for u in q.users_list(ctx.db, q.UsersListParams(organization_id=ctx.org))} |
| backend/src/kotorelay/operations/reviews/list_reviews/functions.py:21 | {v.id: v for v in q.versions_list(ctx.db, q.VersionsListParams(organization_id=ctx.org))} |
| backend/src/kotorelay/operations/reviews/list_reviews/functions.py:48 | [{'submission': s, 'title': versions[s.version_id].title, 'version_number': versions[s.version_id].number, 'requested_by': users[s.requested_by], 'department_name': departments[documents[s.document_id].department_id], 'self_requested': s.requested_by == ctx.user.id, 'can_review': ctx.permission(documents[s.document_id].department_id, 'review')} for s in q.submissions_list(ctx.db, q.SubmissionsListParams(organization_id=ctx.org)) if s.document_id in documents] |
| backend/src/kotorelay/operations/reviews/list_reviews/generated/queries.py:38 | db.query('operations/reviews/list_reviews/sql/001_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/reviews/list_reviews/generated/queries.py:72 | db.query('operations/reviews/list_reviews/sql/002_documents_list.sql', params.model_dump(), DocumentsListRow) |
| backend/src/kotorelay/operations/reviews/list_reviews/generated/queries.py:105 | db.query('operations/reviews/list_reviews/sql/003_submissions_list.sql', params.model_dump(), SubmissionsListRow) |
| backend/src/kotorelay/operations/reviews/list_reviews/generated/queries.py:133 | db.query('operations/reviews/list_reviews/sql/004_users_list.sql', params.model_dump(), UsersListRow) |
| backend/src/kotorelay/operations/reviews/list_reviews/generated/queries.py:164 | db.query('operations/reviews/list_reviews/sql/005_versions_list.sql', params.model_dump(), VersionsListRow) |
| backend/src/kotorelay/operations/reviews/list_reviews/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/reviews/list_reviews/router.py:27 | build_response(f.select_list_reviews(users, departments, documents, versions, ctx)) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:63 | db.query('operations/system/authorization/sql/002_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:176 | db.query('operations/system/authorization/sql/006_memberships_list.sql', params.model_dump(), MembershipsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:220 | db.query('operations/system/authorization/sql/008_organizations_get.sql', params.model_dump(), OrganizationsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:248 | db.query('operations/system/authorization/sql/009_users_list.sql', params.model_dump(), UsersListRow) |
