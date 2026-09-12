<!-- 実装から生成。直接編集しない。入力SHA256: f4209c4ed7b292c6ed57aa300cf25000f8931a1f59b1fb43cfeb436b1d949dbe -->

# 部署の利用数と文書貢献を集計 — unit-test

実在するpytest関数とassertから抽出。パラメータごとの実行成否は品質ポータルで確認します。共有するAPI群の境界試験も含みます。

## 入力・認可・分岐要因

| 場所 | 要因／要素 | 異常結果 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:40 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:43 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:60 | m.department_id == department_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/metrics/functions.py:46 | ctx.permission(department_id, 'manage') | 'forbidden' | 403 |
| backend/src/kotorelay/operations/metrics/functions.py:47 | start.tzinfo is not None and end.tzinfo is not None | 'invalid_period' | 422 |
| backend/src/kotorelay/operations/metrics/functions.py:48 | start < end | 'invalid_period' | 422 |

## Given / When / Then

| 日本語ケース／test node | Given | When | Then（期待状態） |
| --- | --- | --- | --- |
| 閲覧と質問の再送を重複計上しない / backend/tests/test_workflow.py::test_閲覧と質問の再送を重複計上しない | client | client.post('/api/chat', headers=headers('reader', key), json=question) ; client.post('/api/chat', headers=headers('reader', key), json=question) ; client.get(f'/api/metrics/{DEPT}?start=2020-01-01T00:00:00Z&end=2100-01-01T00:00:00Z', headers=headers('leader')) ; client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view) ; client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) | client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view).json()['recorded'] ; not client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view).json()['recorded'] ; a.json() == b.json() ; metrics['questions'] == 1 and metrics['views'] == 1 and (metrics['unique_viewers'] == 1) ; metrics['documents'][0]['contributions'] == 1 ; 'question' not in str(metrics['documents']) |
| 他人の会話と管理統計を拒否する / backend/tests/test_workflow.py::test_他人の会話と管理統計を拒否する | client | client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('leader')) ; client.get(f'/api/metrics/{DEPT}?start=2020-01-01T00:00:00Z&end=2100-01-01T00:00:00Z', headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) | client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('leader')).status_code == 404 ; ask(client, 'author', conversation_id=answer['conversation_id']).status_code == 404 ; client.get(f'/api/metrics/{DEPT}?start=2020-01-01T00:00:00Z&end=2100-01-01T00:00:00Z', headers=headers('reader')).status_code == 403 |
