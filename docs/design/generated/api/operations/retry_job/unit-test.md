<!-- 実装から生成。直接編集しない。入力SHA256: 987c18a693c5fa5c9f59f732c65771f1c047c0829e22a5d72b689276aae93c56 -->

# 反映ジョブを再処理 — 単体テスト詳細

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 0. Router層の暗黙処理

FastAPI/Pydanticの入力検証、認証依存、共通middlewareを適用します。healthは認証不要です。型制約違反は422、認証失敗は401、commit競合は409です。

## 1. 要因ごとの要素

### F01 条件分岐

対象: `backend/src/kotorelay/context.py:41`。式: `bool(organizations) and (not organizations[0].suspended)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F01-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F01-false | 不成立 | 'unauthenticated' / 401 |


### F02 条件分岐

対象: `backend/src/kotorelay/context.py:44`。式: `len(users) == 1`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F02-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F02-false | 不成立 | 'unauthenticated' / 401 |


### F03 条件分岐

対象: `backend/src/kotorelay/context.py:54`。式: `q.organizations_fence(self.db, self.organization) == 1`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F03-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F03-false | 不成立 | 'conflict' / 409 |


### F04 条件分岐

対象: `backend/src/kotorelay/errors.py:13`。式: `not condition`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F04-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F04-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F05 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:41`。式: `doc.latest_version_id != job.version_id or not job.version_id`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F05-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F05-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F06 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:51`。式: `len(stale) > 100`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F06-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F06-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F07 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:53`。式: `doc.status != 'active'`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F07-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F07-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F08 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:71`。式: `len(parts) <= 300`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F08-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F08-false | 不成立 | 'limit' / 422 |


### F09 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:88`。式: `chunk.id in previous`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F09-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F09-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F10 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:93`。式: `len(actual) == len(parts) and engine.verify([c.id for c in actual])`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F10-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F10-false | 不成立 | 'integrity' / 503 |


### F11 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:171`。式: `job.status in {'done', 'obsolete'}`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F11-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F11-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F12 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:166`。式: `ctx.user.operator`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F12-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F12-false | 不成立 | 'forbidden' / 403 |


### F13 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:168`。式: `bool(rows)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F13-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F13-false | 不成立 | not_found / 404 |


### F14 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:170`。式: `job.attempts < 5`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F14-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F14-false | 不成立 | 'limit' / 429 |


### F15 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:102`。式: `doc.status != 'deleted'`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F15-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F15-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F16 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:104`。式: `(now() - job.created_at).total_seconds() < ctx.settings.retention_days * 86400`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F16-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F16-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F17 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:149`。式: `len(target_chunks) > 100`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F17-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F17-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F18 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:154`。式: `len(target_runs) > 100`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F18-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F18-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F19 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:157`。式: `asset.document_id == doc.id`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F19-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F19-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F20 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:160`。式: `draft.document_id == doc.id`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F20-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F20-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F21 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:133`。式: `row.document_id == doc.id`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F21-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F21-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F22 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:135`。式: `row.document_id in live`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F22-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F22-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F23 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:34`。式: `buffer.strip()`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F23-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F23-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F24 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:22`。式: `line.startswith('#') or len(buffer) + len(line) > 1200`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F24-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F24-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F25 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:23`。式: `buffer.strip()`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F25-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F25-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F26 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:26`。式: `line.startswith('#')`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F26-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F26-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F27 条件分岐

対象: `backend/src/kotorelay/operations/indexing/shared/functions.py:30`。式: `len(buffer) + len(part) > 1200 and buffer.strip()`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F27-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F27-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


## 2. 直積したテストケース一覧

参照先と同じ章名を保持しています。ここでは実在するテストを列挙します。要因の完全な直積や到達不能条件の自動証明は実装していないため、全組合せの網羅を示す表ではありません。API群に共通する境界試験を含みます。

| Case ID | 日本語ケース | test node |
| --- | --- | --- |
| TC001 | 審査とジョブの表示名を対象版から得る | backend/tests/test_ui_contract.py::test_審査とジョブの表示名を対象版から得る |
| TC002 | 承認された版だけを引用付きで回答する | backend/tests/test_workflow.py::test_承認された版だけを引用付きで回答する |
| TC003 | 新しい下書きは公開タイトルと本文を変更しない | backend/tests/test_workflow.py::test_新しい下書きは公開タイトルと本文を変更しない |
| TC004 | 新版承認後の未反映期間は旧版を使わない | backend/tests/test_workflow.py::test_新版承認後の未反映期間は旧版を使わない |
| TC005 | 公開停止と削除で回答履歴も失効する | backend/tests/test_workflow.py::test_公開停止と削除で回答履歴も失効する |
| TC006 | 他部署は直接IDと一覧とRAGから取得できない | backend/tests/test_workflow.py::test_他部署は直接IDと一覧とRAGから取得できない |
| TC007 | 共有は閲覧だけを許可する | backend/tests/test_workflow.py::test_共有は閲覧だけを許可する |
| TC008 | 所属停止は古いトークンでも即時反映する | backend/tests/test_workflow.py::test_所属停止は古いトークンでも即時反映する |
| TC009 | 審査の再送は結果とジョブを重複作成しない | backend/tests/test_workflow.py::test_審査の再送は結果とジョブを重複作成しない |
| TC010 | 閲覧と質問の再送を重複計上しない | backend/tests/test_workflow.py::test_閲覧と質問の再送を重複計上しない |
| TC011 | 他人の会話と管理統計を拒否する | backend/tests/test_workflow.py::test_他人の会話と管理統計を拒否する |
| TC012 | 画像のOCR確認をmanifestへ固定する | backend/tests/test_workflow.py::test_画像のOCR確認をmanifestへ固定する |
| TC013 | 非運用者は反映ジョブを操作できない | backend/tests/test_workflow.py::test_非運用者は反映ジョブを操作できない |
| TC014 | 反映失敗を照合し再試行で回復する | backend/tests/test_workflow.py::test_反映失敗を照合し再試行で回復する |
| TC015 | 画像を含む削除を保持期間後に完了する | backend/tests/test_workflow.py::test_画像を含む削除を保持期間後に完了する |
| TC016 | モデル実行中の権限変更で回答を保留する | backend/tests/test_workflow.py::test_モデル実行中の権限変更で回答を保留する |
| TC017 | モデル呼び出し失敗を失敗件数として区別する | backend/tests/test_workflow.py::test_モデル呼び出し失敗を失敗件数として区別する |
| TC018 | 不正な索引来歴をモデルへ渡さない | backend/tests/test_workflow.py::test_不正な索引来歴をモデルへ渡さない |
| TC019 | 失効したジョブは公開版を戻さない | backend/tests/test_workflow.py::test_失効したジョブは公開版を戻さない |
| TC020 | 外部索引失敗を記録して部分完了をreadyにしない | backend/tests/test_workflow.py::test_外部索引失敗を記録して部分完了をreadyにしない |
| TC021 | 回答根拠の欠落と改変は閲覧時に非表示とする | backend/tests/test_workflow.py::test_回答根拠の欠落と改変は閲覧時に非表示とする |
| TC022 | 中断した質問は同じIDで再開し二重計上しない | backend/tests/test_workflow.py::test_中断した質問は同じIDで再開し二重計上しない |
| TC023 | 外部検索は返されたID以外を根拠にしない | backend/tests/test_workflow.py::test_外部検索は返されたID以外を根拠にしない |
| TC024 | モデル入力直前に失効を検知した場合はモデルを呼ばない | backend/tests/test_workflow.py::test_モデル入力直前に失効を検知した場合はモデルを呼ばない |
| TC025 | 削除配送を100行単位で再開し共有本文を残す | backend/tests/test_workflow.py::test_削除配送を100行単位で再開し共有本文を残す |


## 3. テスト詳細

### TC001

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 審査とジョブの表示名を対象版から得る |
| test node | backend/tests/test_ui_contract.py::test_審査とジョブの表示名を対象版から得る |
| Given | client |
| When | client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '未承認名', 'body': '本文', 'revision': 2}) ; client.get('/api/operations/jobs?details=true', headers=headers('operator')) ; client.get('/api/operations/jobs?details=true', headers=headers('reader')) ; client.get('/api/operations/jobs?details=true', headers=headers('operator')) ; client.get('/api/reviews', headers=headers('reviewer')) |
| Then | review['title'] == version['title'] and review['version_number'] == 1 ; review['requested_by'] and review['department_name'] ; jobs[0]['version_number'] == 1 ; client.get('/api/operations/jobs?details=true', headers=headers('reader')).status_code == 403 ; any((j['version_number'] is None for j in jobs)) |


### TC002

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 承認された版だけを引用付きで回答する |
| test node | backend/tests/test_workflow.py::test_承認された版だけを引用付きで回答する |
| Given | client |
| When | client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | result.status_code == 200 ; answer['status'] == 'answered' ; '承認後にリリース' in answer['answer'] ; answer['citations'][0]['version_id'] == version['id'] ; answer['citations'][0]['document_id'] == doc['id'] ; history[0]['answer'] == answer['answer'] |


### TC003

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 新しい下書きは公開タイトルと本文を変更しない |
| test node | backend/tests/test_workflow.py::test_新しい下書きは公開タイトルと本文を変更しない |
| Given | client |
| When | client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '極秘タイトル', 'body': '公開不可', 'revision': 2}) ; client.get('/api/documents', headers=headers('reader')) ; client.get(f"/api/documents/{doc['id']}", headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | client.get('/api/documents', headers=headers('reader')).json()[0]['title'] == '開発ガイド' ; client.get(f"/api/documents/{doc['id']}", headers=headers('reader')).json()['version']['id'] == v1['id'] ; ask(client).json()['status'] == 'answered' |


### TC004

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 新版承認後の未反映期間は旧版を使わない |
| test node | backend/tests/test_workflow.py::test_新版承認後の未反映期間は旧版を使わない |
| Given | client |
| When | client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '新版', 'body': '開発フローを変更しました。', 'revision': 2}) ; client.get(f"/api/documents/{doc['id']}?version_id={v1['id']}", headers=headers('reader')) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) |
| Then | ask(client).json()['status'] == 'held' ; ask(client).json()['citations'][0]['version_id'] == v2['id'] ; client.get(f"/api/documents/{doc['id']}?version_id={v1['id']}", headers=headers('reader')).status_code == 404 |


### TC005

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 公開停止と削除で回答履歴も失効する |
| test node | backend/tests/test_workflow.py::test_公開停止と削除で回答履歴も失効する |
| Given | client, status |
| When | client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('leader'), json={'revision': current['revision'], 'visibility': 'department', 'shared_departments': [], 'status': 'active', 'reason': '検証文書の利用終了', **kwargs}) ; client.get('/api/documents?scope=manage', headers=headers('leader')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | policy(client, doc, status=status).status_code == 200 ; ask(client).json()['status'] == 'held' ; history[0]['status'] == 'hidden' and history[0]['citations'] == [] ; '承認後にリリース' not in history[0]['answer'] |


### TC006

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 他部署は直接IDと一覧とRAGから取得できない |
| test node | backend/tests/test_workflow.py::test_他部署は直接IDと一覧とRAGから取得できない |
| Given | client |
| When | client.get(f"/api/documents/{doc['id']}", headers=headers('other')) ; client.get('/api/documents', headers=headers('other')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | client.get(f"/api/documents/{doc['id']}", headers=headers('other')).status_code == 404 ; client.get('/api/documents', headers=headers('other')).json() == [] ; ask(client, 'other', department_id=OTHER).json()['status'] == 'held' ; ask(client, 'other').status_code == 403 |


### TC007

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 共有は閲覧だけを許可する |
| test node | backend/tests/test_workflow.py::test_共有は閲覧だけを許可する |
| Given | client |
| When | client.get(f"/api/documents/{doc['id']}", headers=headers('other')) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers('other')) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('other'), json={'revision': 1, 'visibility': 'organization', 'status': 'deleted'}) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('leader'), json={'revision': current['revision'], 'visibility': 'department', 'shared_departments': [], 'status': 'active', 'reason': '検証文書の利用終了', **kwargs}) ; client.get('/api/documents?scope=manage', headers=headers('leader')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | policy(client, doc, visibility='selected', shared_departments=[OTHER]).status_code == 200 ; client.get(f"/api/documents/{doc['id']}", headers=headers('other')).status_code == 200 ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers('other')).status_code == 404 ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('other'), json={'revision': 1, 'visibility': 'organization', 'status': 'deleted'}).status_code == 404 |


### TC008

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 所属停止は古いトークンでも即時反映する |
| test node | backend/tests/test_workflow.py::test_所属停止は古いトークンでも即時反映する |
| Given | client |
| When | client.put('/api/groups/memberships', headers=headers('leader'), json={'user_id': stable_id('reader'), 'department_id': DEPT, 'active': False}) ; client.get(f"/api/documents/{doc['id']}", headers=headers('reader')) ; client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | response.status_code == 200 ; client.get(f"/api/documents/{doc['id']}", headers=headers('reader')).status_code == 404 ; client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')).json()[0]['status'] == 'hidden' |


### TC009

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 審査の再送は結果とジョブを重複作成しない |
| test node | backend/tests/test_workflow.py::test_審査の再送は結果とジョブを重複作成しない |
| Given | client |
| When | client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer', key), json=data) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer', key), json=data) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer', key), json=data) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json=data) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) |
| Then | first.json() == second.json() ; len(client.get('/api/operations/jobs', headers=headers('operator')).json()) == 1 ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer', key), json=data).status_code == 409 ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json=data).status_code == 409 |


### TC010

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 閲覧と質問の再送を重複計上しない |
| test node | backend/tests/test_workflow.py::test_閲覧と質問の再送を重複計上しない |
| Given | client |
| When | client.post('/api/chat', headers=headers('reader', key), json=question) ; client.post('/api/chat', headers=headers('reader', key), json=question) ; client.get(f'/api/metrics/{DEPT}?start=2020-01-01T00:00:00Z&end=2100-01-01T00:00:00Z', headers=headers('leader')) ; client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view) ; client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view).json()['recorded'] ; not client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view).json()['recorded'] ; a.json() == b.json() ; metrics['questions'] == 1 and metrics['views'] == 1 and (metrics['unique_viewers'] == 1) ; metrics['documents'][0]['contributions'] == 1 ; 'question' not in str(metrics['documents']) |


### TC011

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 他人の会話と管理統計を拒否する |
| test node | backend/tests/test_workflow.py::test_他人の会話と管理統計を拒否する |
| Given | client |
| When | client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('leader')) ; client.get(f'/api/metrics/{DEPT}?start=2020-01-01T00:00:00Z&end=2100-01-01T00:00:00Z', headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('leader')).status_code == 404 ; ask(client, 'author', conversation_id=answer['conversation_id']).status_code == 404 ; client.get(f'/api/metrics/{DEPT}?start=2020-01-01T00:00:00Z&end=2100-01-01T00:00:00Z', headers=headers('reader')).status_code == 403 |


### TC012

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 画像のOCR確認をmanifestへ固定する |
| test node | backend/tests/test_workflow.py::test_画像のOCR確認をmanifestへ固定する |
| Given | client |
| When | client.post(f"/api/images/documents/{doc['id']}", headers=headers(), files={'file': ('image.png', buf.getvalue(), 'image/png')}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '画像手順', 'body': '画像の開発フロー', 'revision': 2, 'placements': [p]}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '画像手順', 'body': '画像の開発フロー', 'revision': 3, 'placements': [p]}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': 3}) ; client.post(f"/api/images/{asset['id']}/ocr", headers=headers(), json={'regions': [{'text': '承認後に開発を開始', 'x': 0, 'y': 0, 'width': 1, 'height': 1, 'confidence': 1, 'order': 0}], 'confirmed': True}) ; client.get(f"/api/images/{asset['id']}?version_id={version['id']}", headers=headers('reader')) ; client.get(f"/api/images/{asset['id']}", headers=headers('reader')) ; client.get(f"/api/images/ocr/{run['id']}?version_id={version['id']}", headers=headers('reader')) ; client.get(f"/api/images/ocr/{p['ocr_run_id']}", headers=headers()) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('leader'), json={'revision': current['revision'], 'visibility': 'department', 'shared_departments': [], 'status': 'active', 'reason': '検証文書の利用終了', **kwargs}) ; client.get('/api/documents?scope=manage', headers=headers('leader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) |
| Then | upload.status_code == 201 ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': 3}).status_code == 409 ; client.get(f"/api/images/{asset['id']}?version_id={version['id']}", headers=headers('reader')).status_code == 200 ; client.get(f"/api/images/{asset['id']}", headers=headers('reader')).status_code == 404 ; client.get(f"/api/images/ocr/{run['id']}?version_id={version['id']}", headers=headers('reader')).status_code == 404 ; ask(client).json()['status'] == 'answered' ; client.get(f"/api/images/ocr/{p['ocr_run_id']}", headers=headers()).status_code == 200 ; ask(client).status_code == 200 ; ask(client).status_code == 200 |


### TC013

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 非運用者は反映ジョブを操作できない |
| test node | backend/tests/test_workflow.py::test_非運用者は反映ジョブを操作できない |
| Given | client |
| When | client.get('/api/operations/jobs', headers=headers('reader')) ; client.get('/api/operations/reconcile', headers=headers('leader')) |
| Then | client.get('/api/operations/jobs', headers=headers('reader')).status_code == 403 ; client.get('/api/operations/reconcile', headers=headers('leader')).status_code == 403 |


### TC014

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 反映失敗を照合し再試行で回復する |
| test node | backend/tests/test_workflow.py::test_反映失敗を照合し再試行で回復する |
| Given | client, monkeypatch |
| When | client.get('/api/operations/reconcile', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.get('/api/operations/reconcile', headers=headers('operator')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('leader'), json={'revision': current['revision'], 'visibility': 'department', 'shared_departments': [], 'status': 'active', 'reason': '検証文書の利用終了', **kwargs}) ; client.get('/api/documents?scope=manage', headers=headers('leader')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) |
| Then | differences[0]['reason'] == '最新承認版が未反映' ; result['status'] == 'failed' ; ask(client).json()['status'] == 'held' ; result['status'] == 'done' ; ask(client).json()['status'] == 'answered' ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')).json()['attempts'] == 2 ; '停止済み' in client.get('/api/operations/reconcile', headers=headers('operator')).json()[0]['reason'] |


### TC015

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 画像を含む削除を保持期間後に完了する |
| test node | backend/tests/test_workflow.py::test_画像を含む削除を保持期間後に完了する |
| Given | client, db |
| When | client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(url, headers=headers('operator')) ; client.post(url, headers=headers('operator')) ; client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('leader'), json={'revision': current['revision'], 'visibility': 'department', 'shared_departments': [], 'status': 'active', 'reason': '検証文書の利用終了', **kwargs}) ; client.get('/api/documents?scope=manage', headers=headers('leader')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | policy(client, doc, status='deleted').status_code == 200 ; client.post(url, headers=headers('operator')).json()['status'] == 'retained' ; client.post(url, headers=headers('operator')).json()['status'] == 'done' ; not any((c['document_id'] == doc['id'] for c in db.tables['chunks'].values())) ; not any((d['document_id'] == doc['id'] for d in db.tables['drafts'].values())) ; client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')).json()[0]['status'] == 'hidden' |


### TC016

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | モデル実行中の権限変更で回答を保留する |
| test node | backend/tests/test_workflow.py::test_モデル実行中の権限変更で回答を保留する |
| Given | client, monkeypatch |
| When | client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | result['status'] == 'held' and '絶対に送信' not in result['answer'] |


### TC017

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | モデル呼び出し失敗を失敗件数として区別する |
| test node | backend/tests/test_workflow.py::test_モデル呼び出し失敗を失敗件数として区別する |
| Given | client, monkeypatch |
| When | client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | result['status'] == 'failed' and result['citations'] == [] |


### TC018

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 不正な索引来歴をモデルへ渡さない |
| test node | backend/tests/test_workflow.py::test_不正な索引来歴をモデルへ渡さない |
| Given | client, db |
| When | client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | ask(client).json()['status'] == 'held' ; ask(client).json()['status'] == 'held' |


### TC019

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 失効したジョブは公開版を戻さない |
| test node | backend/tests/test_workflow.py::test_失効したジョブは公開版を戻さない |
| Given | client |
| When | client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{old['id']}", headers=headers('operator')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) |
| Then | client.post(f"/api/operations/jobs/{old['id']}", headers=headers('operator')).json()['status'] == 'obsolete' ; ask(client).json()['citations'][0]['version_id'] == v2['id'] |


### TC020

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 外部索引失敗を記録して部分完了をreadyにしない |
| test node | backend/tests/test_workflow.py::test_外部索引失敗を記録して部分完了をreadyにしない |
| Given | client, monkeypatch |
| When | client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) |
| Then | result['status'] == 'failed' and result['error_code'] == 'external_failure' ; ask(client).json()['status'] == 'held' |


### TC021

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 回答根拠の欠落と改変は閲覧時に非表示とする |
| test node | backend/tests/test_workflow.py::test_回答根拠の欠落と改変は閲覧時に非表示とする |
| Given | client, db, target |
| When | client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | result[0]['status'] == 'hidden' and result[0]['citations'] == [] |


### TC022

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 中断した質問は同じIDで再開し二重計上しない |
| test node | backend/tests/test_workflow.py::test_中断した質問は同じIDで再開し二重計上しない |
| Given | client, db |
| When | client.post('/api/chat', headers=headers('reader', key), json=data.model_dump()) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | result.status_code == 200 ; result.json()['conversation_id'] == first.conversation_id ; len([e for e in db.tables['events'].values() if e['kind'] == 'question']) == 1 |


### TC023

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 外部検索は返されたID以外を根拠にしない |
| test node | backend/tests/test_workflow.py::test_外部検索は返されたID以外を根拠にしない |
| Given | client, monkeypatch |
| When | client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | ask(client).json()['status'] == 'held' |


### TC024

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | モデル入力直前に失効を検知した場合はモデルを呼ばない |
| test node | backend/tests/test_workflow.py::test_モデル入力直前に失効を検知した場合はモデルを呼ばない |
| Given | client, monkeypatch |
| When | client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | ask(client).json()['status'] == 'held' |


### TC025

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 削除配送を100行単位で再開し共有本文を残す |
| test node | backend/tests/test_workflow.py::test_削除配送を100行単位で再開し共有本文を残す |
| Given | client, db |
| When | client.get(f"/api/documents/{other['id']}", headers=headers('reader')) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('leader'), json={'revision': current['revision'], 'visibility': 'department', 'shared_departments': [], 'status': 'active', 'reason': '検証文書の利用終了', **kwargs}) ; client.get('/api/documents?scope=manage', headers=headers('leader')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | not [c for c in db.tables['chunks'].values() if c['document_id'] == doc['id']] ; client.get(f"/api/documents/{other['id']}", headers=headers('reader')).status_code == 200 |
