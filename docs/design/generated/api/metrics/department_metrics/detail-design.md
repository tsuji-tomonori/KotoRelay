<!-- 実装から生成。直接編集しない。入力SHA256: 4c18ae62a9b9de513581947abfc60f1ec45b9f631019a142a812724b4695a84b -->

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
| backend/src/kotorelay/context.py:40 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:43 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:60 | m.department_id == department_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/metrics/functions.py:46 | ctx.permission(department_id, 'manage') | 'forbidden' | 403 |
| backend/src/kotorelay/operations/metrics/functions.py:47 | start.tzinfo is not None and end.tzinfo is not None | 'invalid_period' | 422 |
| backend/src/kotorelay/operations/metrics/functions.py:48 | start < end | 'invalid_period' | 422 |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

| query | DB対象 | 処理 |
| --- | --- | --- |
| departments_list | departments | SELECT |
| documents_list | documents | SELECT |
| events_list | events | SELECT |
| memberships_list | memberships | SELECT |
| organizations_get | organizations | SELECT |
| users_list | users | SELECT |

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
| backend/src/kotorelay/context.py:67 | False |
| backend/src/kotorelay/context.py:61 | {'author': m.can_author, 'review': m.can_review, 'manage': m.leader, 'draft': m.can_author or m.can_review}.get(operation, False) |
| backend/src/kotorelay/context.py:18 | datetime.now(UTC) |
| backend/src/kotorelay/generated/queries.py:437 | db.query('operations/groups/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/generated/queries.py:345 | db.query('operations/documents/sql/documents_list.sql', {'organization_id': organization_id}, DocumentsRow) |
| backend/src/kotorelay/generated/queries.py:682 | db.query('operations/metrics/sql/events_list.sql', {'organization_id': organization_id}, EventsRow) |
| backend/src/kotorelay/generated/queries.py:473 | db.query('operations/groups/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/generated/queries.py:492 | db.query('operations/identity/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/generated/queries.py:534 | db.query('operations/identity/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
| backend/src/kotorelay/operations/metrics/functions.py:52 | {'department_id': department_id, 'timezone': 'Asia/Tokyo', 'generated_at': now().astimezone(ZoneInfo('Asia/Tokyo')), 'start': start, 'end': end, 'questions': sum((e.kind == 'question' for e in consumed)), 'views': sum((e.kind == 'view' for e in consumed)), 'unique_viewers': len({e.user_id for e in consumed if e.kind == 'view'}), 'outcomes': {status: sum((e.kind == 'outcome' and e.outcome == status for e in consumed)) for status in ['answered', 'held', 'failed', 'cancelled']}, 'documents': [{'id': d.id, 'title': d.title, 'views': sum((e.kind == 'view' and e.document_id == d.id for e in events)), 'contributions': len({e.answer_id for e in events if e.kind == 'contribution' and e.document_id == d.id})} for d in docs]} |
| backend/src/kotorelay/operations/metrics/router.py:26 | f.summary(ctx, str(department_id), start, end) |
