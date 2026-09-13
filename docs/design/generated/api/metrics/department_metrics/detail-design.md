<!-- 実装から生成。直接編集しない。入力SHA256: 1c655589065a087f66d0ae05a6e0b777b889337ba2d8cca7542a2988c7248164 -->

# 部署の利用数と文書貢献を集計 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: 部署の利用数と文書貢献を集計。

**Headers**

該当する入力はありません。

認証: [{"HTTPBearer": []}]

`HTTPBearer`: `{"type": "http", "scheme": "bearer"}`


**Path Parameters**

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| department_id | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "uuid", "title": "Department Id"} |


**Query Parameters**

| 項目 | 型 | 必須 | 説明 | 制約 |
| --- | --- | --- | --- | --- |
| start | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "date-time", "title": "Start"} |
| end | string | 必須 | OpenAPIの型制約に従う | {"type": "string", "format": "date-time", "title": "End"} |


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
| backend/src/kotorelay/operations/metrics/department_metrics/functions.py:17 | ctx.permission(str(department_id), 'manage') | 'forbidden' | 403 |
| backend/src/kotorelay/operations/metrics/department_metrics/functions.py:22 | start.tzinfo is not None and end.tzinfo is not None | 'invalid_period' | 422 |
| backend/src/kotorelay/operations/metrics/department_metrics/functions.py:27 | start < end | 'invalid_period' | 422 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| kotorelay.operations.metrics.department_metrics.generated.queries.documents_list | documents | SELECT |
| kotorelay.operations.metrics.department_metrics.generated.queries.events_list | events | SELECT |
| kotorelay.operations.system.authorization.generated.queries.departments_list | departments | SELECT |
| kotorelay.operations.system.authorization.generated.queries.memberships_list | memberships | SELECT |
| kotorelay.operations.system.authorization.generated.queries.organizations_get | organizations | SELECT |
| kotorelay.operations.system.authorization.generated.queries.users_list | users | SELECT |

異常時はDB transactionがrollbackします。内容ハッシュ実体は孤立し得るため、公開認可には使いません。配送失敗はoutboxへ記録します。

## 4. 正常系レスポンス

| Status | 説明 | Media type |
| --- | --- | --- |
| 200 | Successful Response | application/json |
| 422 | Validation Error | application/json |

##### `200` Successful Response

型: `object`。定義: `{"type": "object", "additionalProperties": true, "title": "Response Department Metrics"}`


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
| backend/src/kotorelay/context.py:86 | False |
| backend/src/kotorelay/context.py:80 | {'author': m.can_author, 'review': m.can_review, 'manage': m.leader, 'draft': m.can_author or m.can_review}.get(operation, False) |
| backend/src/kotorelay/context.py:19 | datetime.now(UTC) |
| backend/src/kotorelay/operations/metrics/department_metrics/functions.py:66 | {'department_id': str(department_id), 'timezone': 'Asia/Tokyo', 'generated_at': now().astimezone(ZoneInfo('Asia/Tokyo')), 'start': start, 'end': end, 'questions': sum((e.kind == 'question' for e in consumed)), 'views': sum((e.kind == 'view' for e in consumed)), 'unique_viewers': len({e.user_id for e in consumed if e.kind == 'view'}), 'outcomes': {status: sum((e.kind == 'outcome' and e.outcome == status for e in consumed)) for status in ['answered', 'held', 'failed', 'cancelled']}, 'documents': [{'id': d.id, 'title': d.title, 'views': sum((e.kind == 'view' and e.document_id == d.id for e in events)), 'contributions': len({e.answer_id for e in events if e.kind == 'contribution' and e.document_id == d.id})} for d in docs]} |
| backend/src/kotorelay/operations/metrics/department_metrics/functions.py:17 | require(ctx.permission(str(department_id), 'manage'), 'forbidden', 403) |
| backend/src/kotorelay/operations/metrics/department_metrics/functions.py:22 | require(start.tzinfo is not None and end.tzinfo is not None, 'invalid_period', 422) |
| backend/src/kotorelay/operations/metrics/department_metrics/functions.py:45 | [e for e in events if e.department_id == str(department_id)] |
| backend/src/kotorelay/operations/metrics/department_metrics/functions.py:50 | [d for d in q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org)) if d.department_id == str(department_id)] |
| backend/src/kotorelay/operations/metrics/department_metrics/functions.py:34 | [e for e in q.events_list(ctx.db, q.EventsListParams(organization_id=ctx.org)) if start <= e.created_at < end] |
| backend/src/kotorelay/operations/metrics/department_metrics/functions.py:27 | require(start < end, 'invalid_period', 422) |
| backend/src/kotorelay/operations/metrics/department_metrics/generated/queries.py:43 | db.query('operations/metrics/department_metrics/sql/001_documents_list.sql', params.model_dump(), DocumentsListRow) |
| backend/src/kotorelay/operations/metrics/department_metrics/generated/queries.py:74 | db.query('operations/metrics/department_metrics/sql/002_events_list.sql', params.model_dump(), EventsListRow) |
| backend/src/kotorelay/operations/metrics/department_metrics/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/metrics/department_metrics/router.py:34 | build_response(f.build_department_metrics(start, end, department_id, docs, consumed, events)) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:63 | db.query('operations/system/authorization/sql/002_departments_list.sql', params.model_dump(), DepartmentsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:176 | db.query('operations/system/authorization/sql/006_memberships_list.sql', params.model_dump(), MembershipsListRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:220 | db.query('operations/system/authorization/sql/008_organizations_get.sql', params.model_dump(), OrganizationsGetRow) |
| backend/src/kotorelay/operations/system/authorization/generated/queries.py:248 | db.query('operations/system/authorization/sql/009_users_list.sql', params.model_dump(), UsersListRow) |
