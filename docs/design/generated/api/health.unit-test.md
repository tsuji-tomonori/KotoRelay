<!-- 実装から生成。直接編集しない。入力SHA256: 8ddb6b8d66f674570acb431243c0b3f3887134895acc19f3980f35e395ebe090 -->

# 死活確認 — unit-test

実在するpytest関数とassertから抽出。パラメータごとの実行成否は品質ポータルで確認します。共有するAPI群の境界試験も含みます。

## 入力・認可・分岐要因

| 場所 | 要因／要素 | 異常結果 | HTTP |
| --- | --- | --- | --- |

## Given / When / Then

| 日本語ケース／test node | Given | When | Then（期待状態） |
| --- | --- | --- | --- |
| 認可情報の上書き入力を拒否する / backend/tests/test_workflow.py::test_認可情報の上書き入力を拒否する | client | client.post('/api/documents', headers=headers(), json={'title': '無効', 'department_id': DEPT, 'can_author': True}) ; client.get('/api/health') | result.status_code == 422 and 'can_author' not in result.text ; client.get('/api/health').json()['product'] == 'KotoRelay' |
