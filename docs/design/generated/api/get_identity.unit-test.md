<!-- 実装から生成。直接編集しない。入力SHA256: e3cb305ddf380bd9917bab7f5404c8ac54c8511b8d91b58e7192aa0d5991c3cf -->

# 本人と現在の所属権限を取得 — unit-test

実在するpytest関数とassertから抽出。パラメータごとの実行成否は品質ポータルで確認します。共有するAPI群の境界試験も含みます。

## 入力・認可・分岐要因

| 場所 | 要因／要素 | 異常結果 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:40 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:43 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |

## Given / When / Then

| 日本語ケース／test node | Given | When | Then（期待状態） |
| --- | --- | --- | --- |
| 所属停止は古いトークンでも即時反映する / backend/tests/test_workflow.py::test_所属停止は古いトークンでも即時反映する | client | client.put('/api/groups/memberships', headers=headers('leader'), json={'user_id': stable_id('reader'), 'department_id': DEPT, 'active': False}) ; client.get(f"/api/documents/{doc['id']}", headers=headers('reader')) ; client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) | response.status_code == 200 ; client.get(f"/api/documents/{doc['id']}", headers=headers('reader')).status_code == 404 ; client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')).json()[0]['status'] == 'hidden' |
| 自己承認とリーダーの暗黙承認を拒否する / backend/tests/test_workflow.py::test_自己承認とリーダーの暗黙承認を拒否する | client | client.put('/api/groups/memberships', headers=headers('leader'), json={'user_id': stable_id('author'), 'department_id': DEPT, 'can_author': True, 'can_review': True}) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers(persona), json={'manifest_hash': version['manifest_hash'], 'decision': 'approved'}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) | client.post(f"/api/reviews/{review['id']}/decision", headers=headers(persona), json={'manifest_hash': version['manifest_hash'], 'decision': 'approved'}).status_code == code |
| 現行の所属と管理メンバーを取得する / backend/tests/test_workflow.py::test_現行の所属と管理メンバーを取得する | client | client.get('/api/groups/me', headers=headers('author')) ; client.get(f'/api/groups/{DEPT}/members', headers=headers('leader')) ; client.get(f'/api/groups/{DEPT}/members', headers=headers('reader')) ; client.put('/api/groups/memberships', headers=headers('operator'), json={'user_id': stable_id('other'), 'department_id': DEPT, 'can_author': True}) ; client.get('/api/groups/me', headers=headers('other')) | me['user']['display_name'] == '青木 はるか' ; len(members) == 5 ; client.get(f'/api/groups/{DEPT}/members', headers=headers('reader')).status_code == 403 ; client.put('/api/groups/memberships', headers=headers('operator'), json={'user_id': stable_id('other'), 'department_id': DEPT, 'can_author': True}).status_code == 200 ; client.get('/api/groups/me', headers=headers('other')).json()['memberships'][1]['can_author'] is True |
