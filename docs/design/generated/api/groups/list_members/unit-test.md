<!-- 実装から生成。直接編集しない。入力SHA256: 31de213f242d3d7bf0d4f5957d4ef327aaacb2267a973d8e0adce1f1531ac7e1 -->

# 自部署の所属を一覧 — 単体テスト詳細

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 0. Router層の暗黙処理

FastAPI/Pydanticの入力検証、認証依存、共通middlewareを適用します。healthは認証不要です。型制約違反は422、認証失敗は401、commit競合は409です。

## 1. 要因ごとの要素

### F01 条件分岐

対象: `backend/src/kotorelay/context.py:40`。式: `bool(organizations) and (not organizations[0].suspended)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F01-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F01-false | 不成立 | 'unauthenticated' / 401 |


### F02 条件分岐

対象: `backend/src/kotorelay/context.py:43`。式: `len(users) == 1`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F02-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F02-false | 不成立 | 'unauthenticated' / 401 |


### F03 条件分岐

対象: `backend/src/kotorelay/context.py:60`。式: `m.department_id == department_id`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F03-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F03-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F04 条件分岐

対象: `backend/src/kotorelay/errors.py:13`。式: `not condition`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F04-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F04-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F05 条件分岐

対象: `backend/src/kotorelay/operations/groups/functions.py:20`。式: `ctx.permission(department_id, 'manage')`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F05-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F05-false | 不成立 | 'forbidden' / 403 |


## 2. 直積したテストケース一覧

参照先と同じ章名を保持しています。ここでは実在するテストを列挙します。要因の完全な直積や到達不能条件の自動証明は実装していないため、全組合せの網羅を示す表ではありません。API群に共通する境界試験を含みます。

| Case ID | 日本語ケース | test node |
| --- | --- | --- |
| TC001 | 成功応答の送信時には別接続から保存済み文書が見える | backend/tests/test_postgres.py::test_成功応答の送信時には別接続から保存済み文書が見える |
| TC002 | commit時の競合は成功応答を送らず409にしてrollbackする | backend/tests/test_postgres.py::test_commit時の競合は成功応答を送らず409にしてrollbackする |
| TC003 | 複数部署の一覧を権限検査してページング前に絞る | backend/tests/test_ui_contract.py::test_複数部署の一覧を権限検査してページング前に絞る |
| TC004 | 会話内の利用部署変更を拒否し新規会話なら許可する | backend/tests/test_ui_contract.py::test_会話内の利用部署変更を拒否し新規会話なら許可する |
| TC005 | 所属停止は古いトークンでも即時反映する | backend/tests/test_workflow.py::test_所属停止は古いトークンでも即時反映する |
| TC006 | 自己承認とリーダーの暗黙承認を拒否する | backend/tests/test_workflow.py::test_自己承認とリーダーの暗黙承認を拒否する |
| TC007 | 現行の所属と管理メンバーを取得する | backend/tests/test_workflow.py::test_現行の所属と管理メンバーを取得する |


## 3. テスト詳細

### TC001

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 成功応答の送信時には別接続から保存済み文書が見える |
| test node | backend/tests/test_postgres.py::test_成功応答の送信時には別接続から保存済み文書が見える |
| Given | postgres |
| When | client.post('/api/documents', headers=headers(), json={'title': title, 'department_id': department}) ; client.get('/api/groups/me', headers=headers()) |
| Then | observed == [True] ; result.status_code == 201 |


### TC002

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | commit時の競合は成功応答を送らず409にしてrollbackする |
| test node | backend/tests/test_postgres.py::test_commit時の競合は成功応答を送らず409にしてrollbackする |
| Given | postgres, monkeypatch |
| When | client.post('/api/documents', headers=headers(), json={'title': '競合して確定しない文書', 'department_id': department}) ; client.get('/api/groups/me', headers=headers()) |
| Then | result.status_code == 409 ; result.json()['code'] == 'conflict' ; not q.documents_list(db, postgres.organization_id) |


### TC003

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 複数部署の一覧を権限検査してページング前に絞る |
| test node | backend/tests/test_ui_contract.py::test_複数部署の一覧を権限検査してページング前に絞る |
| Given | client |
| When | client.get(f'/api/documents?scope=manage&page=true&department_id={department}&limit=1', headers=headers('leader')) ; client.post('/api/documents', headers=headers('other'), json={'title': '営業部の文書', 'department_id': OTHER}) ; client.get(f'/api/documents?scope=work&department_id={OTHER}', headers=headers('author')) ; client.get(f'/api/documents?scope=manage&department_id={DEPT}', headers=headers('reader')) ; client.put('/api/groups/memberships', headers=headers('operator'), json={'user_id': user, 'department_id': department, **permissions}) ; client.get('/api/groups/me', headers=headers(persona)) |
| Then | pytest.raises / mock assertionで例外・依存先を検証 |


### TC004

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 会話内の利用部署変更を拒否し新規会話なら許可する |
| test node | backend/tests/test_ui_contract.py::test_会話内の利用部署変更を拒否し新規会話なら許可する |
| Given | client |
| When | client.put('/api/groups/memberships', headers=headers('operator'), json={'user_id': user, 'department_id': department, **permissions}) ; client.get('/api/groups/me', headers=headers(persona)) |
| Then | ask(client, conversation_id=first['conversation_id']).status_code == 200 ; changed.status_code == 409 ; fresh.status_code == 200 and fresh.json()['conversation_id'] != first['conversation_id'] |


### TC005

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 所属停止は古いトークンでも即時反映する |
| test node | backend/tests/test_workflow.py::test_所属停止は古いトークンでも即時反映する |
| Given | client |
| When | client.put('/api/groups/memberships', headers=headers('leader'), json={'user_id': stable_id('reader'), 'department_id': DEPT, 'active': False}) ; client.get(f"/api/documents/{doc['id']}", headers=headers('reader')) ; client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | response.status_code == 200 ; client.get(f"/api/documents/{doc['id']}", headers=headers('reader')).status_code == 404 ; client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')).json()[0]['status'] == 'hidden' |


### TC006

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 自己承認とリーダーの暗黙承認を拒否する |
| test node | backend/tests/test_workflow.py::test_自己承認とリーダーの暗黙承認を拒否する |
| Given | client |
| When | client.put('/api/groups/memberships', headers=headers('leader'), json={'user_id': stable_id('author'), 'department_id': DEPT, 'can_author': True, 'can_review': True}) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers(persona), json={'manifest_hash': version['manifest_hash'], 'decision': 'approved'}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) |
| Then | client.post(f"/api/reviews/{review['id']}/decision", headers=headers(persona), json={'manifest_hash': version['manifest_hash'], 'decision': 'approved'}).status_code == code |


### TC007

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 現行の所属と管理メンバーを取得する |
| test node | backend/tests/test_workflow.py::test_現行の所属と管理メンバーを取得する |
| Given | client |
| When | client.get('/api/groups/me', headers=headers('author')) ; client.get(f'/api/groups/{DEPT}/members', headers=headers('leader')) ; client.get(f'/api/groups/{DEPT}/members', headers=headers('reader')) ; client.put('/api/groups/memberships', headers=headers('operator'), json={'user_id': stable_id('other'), 'department_id': DEPT, 'can_author': True}) ; client.get('/api/groups/me', headers=headers('other')) |
| Then | me['user']['display_name'] == '青木 はるか' ; len(members) == 5 ; client.get(f'/api/groups/{DEPT}/members', headers=headers('reader')).status_code == 403 ; client.put('/api/groups/memberships', headers=headers('operator'), json={'user_id': stable_id('other'), 'department_id': DEPT, 'can_author': True}).status_code == 200 ; client.get('/api/groups/me', headers=headers('other')).json()['memberships'][1]['can_author'] is True |
