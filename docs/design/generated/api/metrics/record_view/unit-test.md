<!-- 実装から生成。直接編集しない。入力SHA256: 1c655589065a087f66d0ae05a6e0b777b889337ba2d8cca7542a2988c7248164 -->

# 実閲覧を一意IDで記録 — 単体テスト詳細

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 0. Router層の暗黙処理

FastAPI/Pydanticの入力検証、認証依存、共通middlewareを適用します。healthは認証不要です。型制約違反は422、認証失敗は401、commit競合は409です。

## 1. 要因ごとの要素

### F01 条件分岐

対象: `backend/src/kotorelay/context.py:43`。式: `bool(organizations) and (not organizations[0].suspended)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F01-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F01-false | 不成立 | 'unauthenticated' / 401 |


### F02 条件分岐

対象: `backend/src/kotorelay/context.py:50`。式: `len(users) == 1`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F02-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F02-false | 不成立 | 'unauthenticated' / 401 |


### F03 条件分岐

対象: `backend/src/kotorelay/context.py:103`。式: `bool(rows)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F03-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F03-false | 不成立 | not_found / 404 |


### F04 条件分岐

対象: `backend/src/kotorelay/context.py:110`。式: `allowed`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F04-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F04-false | 不成立 | not_found / 404 |


### F05 条件分岐

対象: `backend/src/kotorelay/context.py:64`。式: `q.organizations_fence(self.db, q.OrganizationsFenceParams.model_validate(self.organization, from_attributes=True)) == 1`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F05-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F05-false | 不成立 | 'conflict' / 409 |


### F06 条件分岐

対象: `backend/src/kotorelay/errors.py:13`。式: `not condition`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F06-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F06-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F07 条件分岐

対象: `backend/src/kotorelay/operations/metrics/record_view/functions.py:29`。式: `ctx.member(data.department_id)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F07-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F07-false | 不成立 | 'forbidden' / 403 |


### F08 条件分岐

対象: `backend/src/kotorelay/operations/metrics/record_view/functions.py:22`。式: `bool(doc.latest_version_id)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F08-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F08-false | 不成立 | not_found / 404 |


### F09 条件分岐

対象: `backend/src/kotorelay/operations/metrics/record_view/functions.py:41`。式: `previous[0].document_id == doc.id and previous[0].department_id == data.department_id and (previous[0].kind == 'view')`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F09-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F09-false | 不成立 | 'idempotency_conflict' / 409 |


### F10 条件分岐

対象: `backend/src/kotorelay/operations/metrics/record_view/router.py:32`。式: `previous`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F10-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F10-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


## 2. 直積したテストケース一覧

参照先と同じ章名を保持しています。ここでは実在するテストを列挙します。要因の完全な直積や到達不能条件の自動証明は実装していないため、全組合せの網羅を示す表ではありません。API群に共通する境界試験を含みます。

| Case ID | 日本語ケース | test node |
| --- | --- | --- |
| TC001 | 閲覧と質問の再送を重複計上しない | backend/tests/test_workflow.py::test_閲覧と質問の再送を重複計上しない |
| TC002 | 他人の会話と管理統計を拒否する | backend/tests/test_workflow.py::test_他人の会話と管理統計を拒否する |


## 3. テスト詳細

### TC001

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 閲覧と質問の再送を重複計上しない |
| test node | backend/tests/test_workflow.py::test_閲覧と質問の再送を重複計上しない |
| Given | client |
| When | client.post('/api/chat', headers=headers('reader', key), json=question) ; client.post('/api/chat', headers=headers('reader', key), json=question) ; client.get(f'/api/metrics/{DEPT}?start=2020-01-01T00:00:00Z&end=2100-01-01T00:00:00Z', headers=headers('leader')) ; client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view) ; client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view).json()['recorded'] ; not client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view).json()['recorded'] ; a.json() == b.json() ; metrics['questions'] == 1 and metrics['views'] == 1 and (metrics['unique_viewers'] == 1) ; metrics['documents'][0]['contributions'] == 1 ; 'question' not in str(metrics['documents']) |


### TC002

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 他人の会話と管理統計を拒否する |
| test node | backend/tests/test_workflow.py::test_他人の会話と管理統計を拒否する |
| Given | client |
| When | client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('leader')) ; client.get(f'/api/metrics/{DEPT}?start=2020-01-01T00:00:00Z&end=2100-01-01T00:00:00Z', headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('leader')).status_code == 404 ; ask(client, 'author', conversation_id=answer['conversation_id']).status_code == 404 ; client.get(f'/api/metrics/{DEPT}?start=2020-01-01T00:00:00Z&end=2100-01-01T00:00:00Z', headers=headers('reader')).status_code == 403 |
