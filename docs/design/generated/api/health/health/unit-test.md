<!-- 実装から生成。直接編集しない。入力SHA256: 31de213f242d3d7bf0d4f5957d4ef327aaacb2267a973d8e0adce1f1531ac7e1 -->

# 死活確認 — 単体テスト詳細

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 0. Router層の暗黙処理

FastAPI/Pydanticの入力検証、認証依存、共通middlewareを適用します。healthは認証不要です。型制約違反は422、認証失敗は401、commit競合は409です。

## 1. 要因ごとの要素

明示的な条件分岐はありません。

## 2. 直積したテストケース一覧

参照先と同じ章名を保持しています。ここでは実在するテストを列挙します。要因の完全な直積や到達不能条件の自動証明は実装していないため、全組合せの網羅を示す表ではありません。API群に共通する境界試験を含みます。

| Case ID | 日本語ケース | test node |
| --- | --- | --- |
| TC001 | 認可情報の上書き入力を拒否する | backend/tests/test_workflow.py::test_認可情報の上書き入力を拒否する |


## 3. テスト詳細

### TC001

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 認可情報の上書き入力を拒否する |
| test node | backend/tests/test_workflow.py::test_認可情報の上書き入力を拒否する |
| Given | client |
| When | client.post('/api/documents', headers=headers(), json={'title': '無効', 'department_id': DEPT, 'can_author': True}) ; client.get('/api/health') |
| Then | result.status_code == 422 and 'can_author' not in result.text ; client.get('/api/health').json()['product'] == 'KotoRelay' |
