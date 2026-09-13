<!-- 実装から生成。直接編集しない。入力SHA256: 987c18a693c5fa5c9f59f732c65771f1c047c0829e22a5d72b689276aae93c56 -->

# 競合を検出して下書きを保存 — 単体テスト詳細

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

対象: `backend/src/kotorelay/context.py:83`。式: `bool(rows)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F03-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F03-false | 不成立 | not_found / 404 |


### F04 条件分岐

対象: `backend/src/kotorelay/context.py:90`。式: `allowed`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F04-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F04-false | 不成立 | not_found / 404 |


### F05 条件分岐

対象: `backend/src/kotorelay/context.py:54`。式: `q.organizations_fence(self.db, self.organization) == 1`

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

対象: `backend/src/kotorelay/operations/documents/save_draft/functions.py:18`。式: `row.revision == data.revision`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F07-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F07-false | 不成立 | 'conflict' / 409 |


### F08 条件分岐

対象: `backend/src/kotorelay/operations/documents/save_draft/functions.py:44`。式: `len({p.id for p in data.placements}) == len(data.placements)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F08-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F08-false | 不成立 | 'invalid_placement' / 422 |


### F09 条件分岐

対象: `backend/src/kotorelay/operations/documents/save_draft/functions.py:48`。式: `bool(assets) and bool(runs)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F09-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F09-false | 不成立 | 'invalid_placement' / 422 |


### F10 条件分岐

対象: `backend/src/kotorelay/operations/documents/save_draft/functions.py:49`。式: `assets[0].document_id == doc.id and runs[0].asset_id == assets[0].id and (runs[0].document_id == doc.id) and (placement.offset <= len(data.body))`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F10-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F10-false | 不成立 | 'invalid_placement' / 422 |


## 2. 直積したテストケース一覧

参照先と同じ章名を保持しています。ここでは実在するテストを列挙します。要因の完全な直積や到達不能条件の自動証明は実装していないため、全組合せの網羅を示す表ではありません。API群に共通する境界試験を含みます。

| Case ID | 日本語ケース | test node |
| --- | --- | --- |
| TC001 | PostgreSQLで承認とoutboxと回答を一貫して確定する | backend/tests/test_postgres.py::test_PostgreSQLで承認とoutboxと回答を一貫して確定する |
| TC002 | 成功応答の送信時には別接続から保存済み文書が見える | backend/tests/test_postgres.py::test_成功応答の送信時には別接続から保存済み文書が見える |
| TC003 | commit時の競合は成功応答を送らず409にしてrollbackする | backend/tests/test_postgres.py::test_commit時の競合は成功応答を送らず409にしてrollbackする |
| TC004 | 複数部署の一覧を権限検査してページング前に絞る | backend/tests/test_ui_contract.py::test_複数部署の一覧を権限検査してページング前に絞る |
| TC005 | 一覧は公開版と審査版を分離し続きの有無を返す | backend/tests/test_ui_contract.py::test_一覧は公開版と審査版を分離し続きの有無を返す |
| TC006 | 代替テキストと絵文字位置を承認版へ固定する | backend/tests/test_ui_contract.py::test_代替テキストと絵文字位置を承認版へ固定する |
| TC007 | 審査とジョブの表示名を対象版から得る | backend/tests/test_ui_contract.py::test_審査とジョブの表示名を対象版から得る |
| TC008 | Markdownの空白改行を保存してコードポイント位置を維持する | backend/tests/test_ui_contract.py::test_Markdownの空白改行を保存してコードポイント位置を維持する |
| TC009 | 保存と再読込でMarkdownを維持する | backend/tests/test_workflow.py::test_保存と再読込でMarkdownを維持する |
| TC010 | 競合保存は先行内容を上書きしない | backend/tests/test_workflow.py::test_競合保存は先行内容を上書きしない |
| TC011 | 下書きの本文と履歴を担当外に返さない | backend/tests/test_workflow.py::test_下書きの本文と履歴を担当外に返さない |
| TC012 | 未承認文書は閲覧と検索へ現れない | backend/tests/test_workflow.py::test_未承認文書は閲覧と検索へ現れない |
| TC013 | 承認された版だけを引用付きで回答する | backend/tests/test_workflow.py::test_承認された版だけを引用付きで回答する |
| TC014 | 却下理由と不変版を履歴に残す | backend/tests/test_workflow.py::test_却下理由と不変版を履歴に残す |
| TC015 | 新しい下書きは公開タイトルと本文を変更しない | backend/tests/test_workflow.py::test_新しい下書きは公開タイトルと本文を変更しない |
| TC016 | 新版承認後の未反映期間は旧版を使わない | backend/tests/test_workflow.py::test_新版承認後の未反映期間は旧版を使わない |
| TC017 | 公開停止と削除で回答履歴も失効する | backend/tests/test_workflow.py::test_公開停止と削除で回答履歴も失効する |
| TC018 | 他部署は直接IDと一覧とRAGから取得できない | backend/tests/test_workflow.py::test_他部署は直接IDと一覧とRAGから取得できない |
| TC019 | 共有は閲覧だけを許可する | backend/tests/test_workflow.py::test_共有は閲覧だけを許可する |
| TC020 | 所属停止は古いトークンでも即時反映する | backend/tests/test_workflow.py::test_所属停止は古いトークンでも即時反映する |
| TC021 | 審査の再送は結果とジョブを重複作成しない | backend/tests/test_workflow.py::test_審査の再送は結果とジョブを重複作成しない |
| TC022 | 申請の再送で版番号を重複発行しない | backend/tests/test_workflow.py::test_申請の再送で版番号を重複発行しない |
| TC023 | 自己承認とリーダーの暗黙承認を拒否する | backend/tests/test_workflow.py::test_自己承認とリーダーの暗黙承認を拒否する |
| TC024 | 未確認manifestと理由のない却下を拒否する | backend/tests/test_workflow.py::test_未確認manifestと理由のない却下を拒否する |
| TC025 | 古い版の遅着承認でも公開版は戻らない | backend/tests/test_workflow.py::test_古い版の遅着承認でも公開版は戻らない |
| TC026 | 閲覧と質問の再送を重複計上しない | backend/tests/test_workflow.py::test_閲覧と質問の再送を重複計上しない |
| TC027 | 他人の会話と管理統計を拒否する | backend/tests/test_workflow.py::test_他人の会話と管理統計を拒否する |
| TC028 | 画像のOCR確認をmanifestへ固定する | backend/tests/test_workflow.py::test_画像のOCR確認をmanifestへ固定する |
| TC029 | 不正画像を拒否する | backend/tests/test_workflow.py::test_不正画像を拒否する |
| TC030 | 未認証要求を拒否する | backend/tests/test_workflow.py::test_未認証要求を拒否する |
| TC031 | 認可情報の上書き入力を拒否する | backend/tests/test_workflow.py::test_認可情報の上書き入力を拒否する |
| TC032 | 反映失敗を照合し再試行で回復する | backend/tests/test_workflow.py::test_反映失敗を照合し再試行で回復する |
| TC033 | 画像を含む削除を保持期間後に完了する | backend/tests/test_workflow.py::test_画像を含む削除を保持期間後に完了する |
| TC034 | モデル実行中の権限変更で回答を保留する | backend/tests/test_workflow.py::test_モデル実行中の権限変更で回答を保留する |
| TC035 | モデル呼び出し失敗を失敗件数として区別する | backend/tests/test_workflow.py::test_モデル呼び出し失敗を失敗件数として区別する |
| TC036 | 不正な索引来歴をモデルへ渡さない | backend/tests/test_workflow.py::test_不正な索引来歴をモデルへ渡さない |
| TC037 | 失効したジョブは公開版を戻さない | backend/tests/test_workflow.py::test_失効したジョブは公開版を戻さない |
| TC038 | 外部索引失敗を記録して部分完了をreadyにしない | backend/tests/test_workflow.py::test_外部索引失敗を記録して部分完了をreadyにしない |
| TC039 | workerが未配送ジョブを処理する | backend/tests/test_workflow.py::test_workerが未配送ジョブを処理する |
| TC040 | 回答根拠の欠落と改変は閲覧時に非表示とする | backend/tests/test_workflow.py::test_回答根拠の欠落と改変は閲覧時に非表示とする |
| TC041 | 中断した質問は同じIDで再開し二重計上しない | backend/tests/test_workflow.py::test_中断した質問は同じIDで再開し二重計上しない |
| TC042 | 外部検索は返されたID以外を根拠にしない | backend/tests/test_workflow.py::test_外部検索は返されたID以外を根拠にしない |
| TC043 | モデル入力直前に失効を検知した場合はモデルを呼ばない | backend/tests/test_workflow.py::test_モデル入力直前に失効を検知した場合はモデルを呼ばない |
| TC044 | 削除配送を100行単位で再開し共有本文を残す | backend/tests/test_workflow.py::test_削除配送を100行単位で再開し共有本文を残す |
| TC045 | HTTP処理ログを通常のINFO設定で出力し本文とトークンを含めない | backend/tests/test_workflow.py::test_HTTP処理ログを通常のINFO設定で出力し本文とトークンを含めない |


## 3. テスト詳細

### TC001

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | PostgreSQLで承認とoutboxと回答を一貫して確定する |
| test node | backend/tests/test_postgres.py::test_PostgreSQLで承認とoutboxと回答を一貫して確定する |
| Given | postgres |
| When | client.get(f"/api/documents/{doc['id']}", headers=headers('other')) |
| Then | result['status'] == 'answered' and result['citations'][0]['version_id'] == version['id'] ; client.get(f"/api/documents/{doc['id']}", headers=headers('other')).status_code == 404 |


### TC002

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 成功応答の送信時には別接続から保存済み文書が見える |
| test node | backend/tests/test_postgres.py::test_成功応答の送信時には別接続から保存済み文書が見える |
| Given | postgres |
| When | client.post('/api/documents', headers=headers(), json={'title': title, 'department_id': department}) ; client.get('/api/groups/me', headers=headers()) |
| Then | observed == [True] ; result.status_code == 201 |


### TC003

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | commit時の競合は成功応答を送らず409にしてrollbackする |
| test node | backend/tests/test_postgres.py::test_commit時の競合は成功応答を送らず409にしてrollbackする |
| Given | postgres, monkeypatch |
| When | client.post('/api/documents', headers=headers(), json={'title': '競合して確定しない文書', 'department_id': department}) ; client.get('/api/groups/me', headers=headers()) |
| Then | result.status_code == 409 ; result.json()['code'] == 'conflict' ; not q.documents_list(db, postgres.organization_id) |


### TC004

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 複数部署の一覧を権限検査してページング前に絞る |
| test node | backend/tests/test_ui_contract.py::test_複数部署の一覧を権限検査してページング前に絞る |
| Given | client |
| When | client.get(f'/api/documents?scope=manage&page=true&department_id={department}&limit=1', headers=headers('leader')) ; client.post('/api/documents', headers=headers('other'), json={'title': '営業部の文書', 'department_id': OTHER}) ; client.get(f'/api/documents?scope=work&department_id={OTHER}', headers=headers('author')) ; client.get(f'/api/documents?scope=manage&department_id={DEPT}', headers=headers('reader')) ; client.put('/api/groups/memberships', headers=headers('operator'), json={'user_id': user, 'department_id': department, **permissions}) ; client.get('/api/groups/me', headers=headers(persona)) |
| Then | pytest.raises / mock assertionで例外・依存先を検証 |


### TC005

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 一覧は公開版と審査版を分離し続きの有無を返す |
| test node | backend/tests/test_ui_contract.py::test_一覧は公開版と審査版を分離し続きの有無を返す |
| Given | client |
| When | client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '未承認タイトル', 'body': '未承認本文', 'revision': current['revision']}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.get('/api/documents?scope=manage&page=true&status=withdrawn', headers=headers('leader')) ; client.get('/api/documents?page=true&search=不存在', headers=headers('reader')) ; client.get('/api/documents?page=true', headers=headers('reader')) ; client.get('/api/documents?scope=work&page=true', headers=headers()) ; client.get('/api/documents?scope=work&page=true&limit=1', headers=headers()) ; client.get('/api/documents?scope=work&page=true&limit=1&offset=1', headers=headers()) |
| Then | read['title'] == version['title'] and '未承認' not in read['summary'] ; read['published_number'] == 1 and read['index_ready'] is True ; read['review_status'] is None and read['approved_at'] ; work['review_number'] == next_version['number'] and work['review_status'] == 'pending' ; client.get('/api/documents?scope=work&page=true&limit=1', headers=headers()).json()['has_next'] is True ; client.get('/api/documents?scope=work&page=true&limit=1&offset=1', headers=headers()).json()['has_next'] is False ; [d['id'] for d in filtered['items']] == [doc['id']] ; client.get('/api/documents?page=true&search=不存在', headers=headers('reader')).json() == {'items': [], 'has_next': False} |


### TC006

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 代替テキストと絵文字位置を承認版へ固定する |
| test node | backend/tests/test_ui_contract.py::test_代替テキストと絵文字位置を承認版へ固定する |
| Given | client |
| When | client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '画像手順', 'body': '日😀本文', 'revision': 2, 'placements': [placement]}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '次版', 'body': '日😀本文', 'revision': 3, 'placements': [placement]}) ; client.get(f"/api/documents/{doc['id']}", headers=headers('reader')) ; client.post(f"/api/images/{data['asset']['id']}/ocr", headers=headers(), json={'regions': [], 'confirmed': True}) ; client.post(f"/api/images/documents/{doc['id']}", headers=headers(), files={'file': ('x.png', buf.getvalue(), 'image/png')}) |
| Then | saved.status_code == 200 ; json.loads(version['manifest'])['images'][0]['placement'] == placement ; json.loads(old['version']['manifest'])['images'][0]['placement']['alt_text'] == '受付から承認へ進む図' |


### TC007

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 審査とジョブの表示名を対象版から得る |
| test node | backend/tests/test_ui_contract.py::test_審査とジョブの表示名を対象版から得る |
| Given | client |
| When | client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '未承認名', 'body': '本文', 'revision': 2}) ; client.get('/api/operations/jobs?details=true', headers=headers('operator')) ; client.get('/api/operations/jobs?details=true', headers=headers('reader')) ; client.get('/api/operations/jobs?details=true', headers=headers('operator')) ; client.get('/api/reviews', headers=headers('reviewer')) |
| Then | review['title'] == version['title'] and review['version_number'] == 1 ; review['requested_by'] and review['department_name'] ; jobs[0]['version_number'] == 1 ; client.get('/api/operations/jobs?details=true', headers=headers('reader')).status_code == 403 ; any((j['version_number'] is None for j in jobs)) |


### TC008

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | Markdownの空白改行を保存してコードポイント位置を維持する |
| test node | backend/tests/test_ui_contract.py::test_Markdownの空白改行を保存してコードポイント位置を維持する |
| Given | client |
| When | client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '  手順  ', 'body': body, 'revision': 2}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '  ', 'body': body, 'revision': 3}) |
| Then | saved.status_code == 200 ; saved.json()['body'] == body and saved.json()['document']['title'] == '手順' ; invalid.status_code == 422 |


### TC009

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 保存と再読込でMarkdownを維持する |
| test node | backend/tests/test_workflow.py::test_保存と再読込でMarkdownを維持する |
| Given | client |
| When | client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) |
| Then | response.json()['body'] == '# 開発フロー\n承認後にリリースします。' ; response.json()['revision'] == 2 ; response.headers['cache-control'] == 'no-store' |


### TC010

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 競合保存は先行内容を上書きしない |
| test node | backend/tests/test_workflow.py::test_競合保存は先行内容を上書きしない |
| Given | client |
| When | client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '改変', 'body': '消えない', 'revision': 1}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) |
| Then | result.status_code == 409 ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()).json()['body'].startswith('# 開発') |


### TC011

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 下書きの本文と履歴を担当外に返さない |
| test node | backend/tests/test_workflow.py::test_下書きの本文と履歴を担当外に返さない |
| Given | client, persona |
| When | client.get(f"/api/documents/{doc['id']}/{suffix}", headers=headers(persona)) ; client.get('/api/documents?scope=work', headers=headers(persona)) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) |
| Then | client.get('/api/documents?scope=work', headers=headers(persona)).json() == [] ; client.get(f"/api/documents/{doc['id']}/{suffix}", headers=headers(persona)).status_code == 404 |


### TC012

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 未承認文書は閲覧と検索へ現れない |
| test node | backend/tests/test_workflow.py::test_未承認文書は閲覧と検索へ現れない |
| Given | client |
| When | client.get(f"/api/documents/{doc['id']}", headers=headers('reader')) ; client.get('/api/documents', headers=headers('reader')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) |
| Then | client.get('/api/documents', headers=headers('reader')).json() == [] ; client.get(f"/api/documents/{doc['id']}", headers=headers('reader')).status_code == 404 ; result['status'] == 'held' and result['citations'] == [] |


### TC013

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 承認された版だけを引用付きで回答する |
| test node | backend/tests/test_workflow.py::test_承認された版だけを引用付きで回答する |
| Given | client |
| When | client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | result.status_code == 200 ; answer['status'] == 'answered' ; '承認後にリリース' in answer['answer'] ; answer['citations'][0]['version_id'] == version['id'] ; answer['citations'][0]['document_id'] == doc['id'] ; history[0]['answer'] == answer['answer'] |


### TC014

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 却下理由と不変版を履歴に残す |
| test node | backend/tests/test_workflow.py::test_却下理由と不変版を履歴に残す |
| Given | client |
| When | client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '改訂', 'body': '# 開発フロー\n説明を追加。', 'revision': 2}) ; client.get(f"/api/documents/{doc['id']}/history", headers=headers()) ; client.get(f"/api/documents/{doc['id']}/diff?left={v1['id']}&right={v2['id']}", headers=headers()) ; client.put(f"/api/documents/{doc['id']}/versions/{v1['id']}", headers=headers(), json={}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) |
| Then | client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '改訂', 'body': '# 開発フロー\n説明を追加。', 'revision': 2}).status_code == 200 ; v1['id'] != v2['id'] and v2['number'] == 2 ; history[1]['submission']['reason'] == '説明を追加してください' ; '+説明を追加。' in diff['diff'] and '-承認後にリリースします。' in diff['diff'] ; client.put(f"/api/documents/{doc['id']}/versions/{v1['id']}", headers=headers(), json={}).status_code == 404 |


### TC015

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 新しい下書きは公開タイトルと本文を変更しない |
| test node | backend/tests/test_workflow.py::test_新しい下書きは公開タイトルと本文を変更しない |
| Given | client |
| When | client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '極秘タイトル', 'body': '公開不可', 'revision': 2}) ; client.get('/api/documents', headers=headers('reader')) ; client.get(f"/api/documents/{doc['id']}", headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | client.get('/api/documents', headers=headers('reader')).json()[0]['title'] == '開発ガイド' ; client.get(f"/api/documents/{doc['id']}", headers=headers('reader')).json()['version']['id'] == v1['id'] ; ask(client).json()['status'] == 'answered' |


### TC016

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 新版承認後の未反映期間は旧版を使わない |
| test node | backend/tests/test_workflow.py::test_新版承認後の未反映期間は旧版を使わない |
| Given | client |
| When | client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '新版', 'body': '開発フローを変更しました。', 'revision': 2}) ; client.get(f"/api/documents/{doc['id']}?version_id={v1['id']}", headers=headers('reader')) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) |
| Then | ask(client).json()['status'] == 'held' ; ask(client).json()['citations'][0]['version_id'] == v2['id'] ; client.get(f"/api/documents/{doc['id']}?version_id={v1['id']}", headers=headers('reader')).status_code == 404 |


### TC017

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 公開停止と削除で回答履歴も失効する |
| test node | backend/tests/test_workflow.py::test_公開停止と削除で回答履歴も失効する |
| Given | client, status |
| When | client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('leader'), json={'revision': current['revision'], 'visibility': 'department', 'shared_departments': [], 'status': 'active', 'reason': '検証文書の利用終了', **kwargs}) ; client.get('/api/documents?scope=manage', headers=headers('leader')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | policy(client, doc, status=status).status_code == 200 ; ask(client).json()['status'] == 'held' ; history[0]['status'] == 'hidden' and history[0]['citations'] == [] ; '承認後にリリース' not in history[0]['answer'] |


### TC018

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 他部署は直接IDと一覧とRAGから取得できない |
| test node | backend/tests/test_workflow.py::test_他部署は直接IDと一覧とRAGから取得できない |
| Given | client |
| When | client.get(f"/api/documents/{doc['id']}", headers=headers('other')) ; client.get('/api/documents', headers=headers('other')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | client.get(f"/api/documents/{doc['id']}", headers=headers('other')).status_code == 404 ; client.get('/api/documents', headers=headers('other')).json() == [] ; ask(client, 'other', department_id=OTHER).json()['status'] == 'held' ; ask(client, 'other').status_code == 403 |


### TC019

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 共有は閲覧だけを許可する |
| test node | backend/tests/test_workflow.py::test_共有は閲覧だけを許可する |
| Given | client |
| When | client.get(f"/api/documents/{doc['id']}", headers=headers('other')) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers('other')) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('other'), json={'revision': 1, 'visibility': 'organization', 'status': 'deleted'}) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('leader'), json={'revision': current['revision'], 'visibility': 'department', 'shared_departments': [], 'status': 'active', 'reason': '検証文書の利用終了', **kwargs}) ; client.get('/api/documents?scope=manage', headers=headers('leader')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | policy(client, doc, visibility='selected', shared_departments=[OTHER]).status_code == 200 ; client.get(f"/api/documents/{doc['id']}", headers=headers('other')).status_code == 200 ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers('other')).status_code == 404 ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('other'), json={'revision': 1, 'visibility': 'organization', 'status': 'deleted'}).status_code == 404 |


### TC020

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 所属停止は古いトークンでも即時反映する |
| test node | backend/tests/test_workflow.py::test_所属停止は古いトークンでも即時反映する |
| Given | client |
| When | client.put('/api/groups/memberships', headers=headers('leader'), json={'user_id': stable_id('reader'), 'department_id': DEPT, 'active': False}) ; client.get(f"/api/documents/{doc['id']}", headers=headers('reader')) ; client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | response.status_code == 200 ; client.get(f"/api/documents/{doc['id']}", headers=headers('reader')).status_code == 404 ; client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')).json()[0]['status'] == 'hidden' |


### TC021

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 審査の再送は結果とジョブを重複作成しない |
| test node | backend/tests/test_workflow.py::test_審査の再送は結果とジョブを重複作成しない |
| Given | client |
| When | client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer', key), json=data) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer', key), json=data) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer', key), json=data) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json=data) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) |
| Then | first.json() == second.json() ; len(client.get('/api/operations/jobs', headers=headers('operator')).json()) == 1 ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer', key), json=data).status_code == 409 ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json=data).status_code == 409 |


### TC022

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 申請の再送で版番号を重複発行しない |
| test node | backend/tests/test_workflow.py::test_申請の再送で版番号を重複発行しない |
| Given | client |
| When | client.post(url, headers=headers(key=key), json={'revision': 2}) ; client.post(url, headers=headers(key=key), json={'revision': 2}) ; client.get(f"/api/documents/{doc['id']}/history", headers=headers()) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) |
| Then | a.json() == b.json() ; len(client.get(f"/api/documents/{doc['id']}/history", headers=headers()).json()) == 1 |


### TC023

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 自己承認とリーダーの暗黙承認を拒否する |
| test node | backend/tests/test_workflow.py::test_自己承認とリーダーの暗黙承認を拒否する |
| Given | client |
| When | client.put('/api/groups/memberships', headers=headers('leader'), json={'user_id': stable_id('author'), 'department_id': DEPT, 'can_author': True, 'can_review': True}) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers(persona), json={'manifest_hash': version['manifest_hash'], 'decision': 'approved'}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) |
| Then | client.post(f"/api/reviews/{review['id']}/decision", headers=headers(persona), json={'manifest_hash': version['manifest_hash'], 'decision': 'approved'}).status_code == code |


### TC024

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 未確認manifestと理由のない却下を拒否する |
| test node | backend/tests/test_workflow.py::test_未確認manifestと理由のない却下を拒否する |
| Given | client, data |
| When | client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'manifest_hash': version['manifest_hash'], **data}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) |
| Then | result.status_code in [409, 422] |


### TC025

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 古い版の遅着承認でも公開版は戻らない |
| test node | backend/tests/test_workflow.py::test_古い版の遅着承認でも公開版は戻らない |
| Given | client |
| When | client.get(f"/api/documents/{doc['id']}", headers=headers('reader')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) |
| Then | client.get(f"/api/documents/{doc['id']}", headers=headers('reader')).json()['version']['id'] == v2['id'] |


### TC026

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 閲覧と質問の再送を重複計上しない |
| test node | backend/tests/test_workflow.py::test_閲覧と質問の再送を重複計上しない |
| Given | client |
| When | client.post('/api/chat', headers=headers('reader', key), json=question) ; client.post('/api/chat', headers=headers('reader', key), json=question) ; client.get(f'/api/metrics/{DEPT}?start=2020-01-01T00:00:00Z&end=2100-01-01T00:00:00Z', headers=headers('leader')) ; client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view) ; client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view).json()['recorded'] ; not client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view).json()['recorded'] ; a.json() == b.json() ; metrics['questions'] == 1 and metrics['views'] == 1 and (metrics['unique_viewers'] == 1) ; metrics['documents'][0]['contributions'] == 1 ; 'question' not in str(metrics['documents']) |


### TC027

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 他人の会話と管理統計を拒否する |
| test node | backend/tests/test_workflow.py::test_他人の会話と管理統計を拒否する |
| Given | client |
| When | client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('leader')) ; client.get(f'/api/metrics/{DEPT}?start=2020-01-01T00:00:00Z&end=2100-01-01T00:00:00Z', headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('leader')).status_code == 404 ; ask(client, 'author', conversation_id=answer['conversation_id']).status_code == 404 ; client.get(f'/api/metrics/{DEPT}?start=2020-01-01T00:00:00Z&end=2100-01-01T00:00:00Z', headers=headers('reader')).status_code == 403 |


### TC028

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 画像のOCR確認をmanifestへ固定する |
| test node | backend/tests/test_workflow.py::test_画像のOCR確認をmanifestへ固定する |
| Given | client |
| When | client.post(f"/api/images/documents/{doc['id']}", headers=headers(), files={'file': ('image.png', buf.getvalue(), 'image/png')}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '画像手順', 'body': '画像の開発フロー', 'revision': 2, 'placements': [p]}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '画像手順', 'body': '画像の開発フロー', 'revision': 3, 'placements': [p]}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': 3}) ; client.post(f"/api/images/{asset['id']}/ocr", headers=headers(), json={'regions': [{'text': '承認後に開発を開始', 'x': 0, 'y': 0, 'width': 1, 'height': 1, 'confidence': 1, 'order': 0}], 'confirmed': True}) ; client.get(f"/api/images/{asset['id']}?version_id={version['id']}", headers=headers('reader')) ; client.get(f"/api/images/{asset['id']}", headers=headers('reader')) ; client.get(f"/api/images/ocr/{run['id']}?version_id={version['id']}", headers=headers('reader')) ; client.get(f"/api/images/ocr/{p['ocr_run_id']}", headers=headers()) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('leader'), json={'revision': current['revision'], 'visibility': 'department', 'shared_departments': [], 'status': 'active', 'reason': '検証文書の利用終了', **kwargs}) ; client.get('/api/documents?scope=manage', headers=headers('leader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) |
| Then | upload.status_code == 201 ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': 3}).status_code == 409 ; client.get(f"/api/images/{asset['id']}?version_id={version['id']}", headers=headers('reader')).status_code == 200 ; client.get(f"/api/images/{asset['id']}", headers=headers('reader')).status_code == 404 ; client.get(f"/api/images/ocr/{run['id']}?version_id={version['id']}", headers=headers('reader')).status_code == 404 ; ask(client).json()['status'] == 'answered' ; client.get(f"/api/images/ocr/{p['ocr_run_id']}", headers=headers()).status_code == 200 ; ask(client).status_code == 200 ; ask(client).status_code == 200 |


### TC029

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 不正画像を拒否する |
| test node | backend/tests/test_workflow.py::test_不正画像を拒否する |
| Given | client, payload |
| When | client.post(f"/api/images/documents/{doc['id']}", headers=headers(), files={'file': ('bad.png', payload, 'image/png')}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) |
| Then | client.post(f"/api/images/documents/{doc['id']}", headers=headers(), files={'file': ('bad.png', payload, 'image/png')}).status_code == 422 |


### TC030

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 未認証要求を拒否する |
| test node | backend/tests/test_workflow.py::test_未認証要求を拒否する |
| Given | client, token |
| When | client.get('/api/documents', headers={'Authorization': token}) |
| Then | client.get('/api/documents', headers={'Authorization': token}).status_code == 401 |


### TC031

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 認可情報の上書き入力を拒否する |
| test node | backend/tests/test_workflow.py::test_認可情報の上書き入力を拒否する |
| Given | client |
| When | client.post('/api/documents', headers=headers(), json={'title': '無効', 'department_id': DEPT, 'can_author': True}) ; client.get('/api/health') |
| Then | result.status_code == 422 and 'can_author' not in result.text ; client.get('/api/health').json()['product'] == 'KotoRelay' |


### TC032

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 反映失敗を照合し再試行で回復する |
| test node | backend/tests/test_workflow.py::test_反映失敗を照合し再試行で回復する |
| Given | client, monkeypatch |
| When | client.get('/api/operations/reconcile', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.get('/api/operations/reconcile', headers=headers('operator')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('leader'), json={'revision': current['revision'], 'visibility': 'department', 'shared_departments': [], 'status': 'active', 'reason': '検証文書の利用終了', **kwargs}) ; client.get('/api/documents?scope=manage', headers=headers('leader')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) |
| Then | differences[0]['reason'] == '最新承認版が未反映' ; result['status'] == 'failed' ; ask(client).json()['status'] == 'held' ; result['status'] == 'done' ; ask(client).json()['status'] == 'answered' ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')).json()['attempts'] == 2 ; '停止済み' in client.get('/api/operations/reconcile', headers=headers('operator')).json()[0]['reason'] |


### TC033

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 画像を含む削除を保持期間後に完了する |
| test node | backend/tests/test_workflow.py::test_画像を含む削除を保持期間後に完了する |
| Given | client, db |
| When | client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(url, headers=headers('operator')) ; client.post(url, headers=headers('operator')) ; client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('leader'), json={'revision': current['revision'], 'visibility': 'department', 'shared_departments': [], 'status': 'active', 'reason': '検証文書の利用終了', **kwargs}) ; client.get('/api/documents?scope=manage', headers=headers('leader')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | policy(client, doc, status='deleted').status_code == 200 ; client.post(url, headers=headers('operator')).json()['status'] == 'retained' ; client.post(url, headers=headers('operator')).json()['status'] == 'done' ; not any((c['document_id'] == doc['id'] for c in db.tables['chunks'].values())) ; not any((d['document_id'] == doc['id'] for d in db.tables['drafts'].values())) ; client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')).json()[0]['status'] == 'hidden' |


### TC034

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | モデル実行中の権限変更で回答を保留する |
| test node | backend/tests/test_workflow.py::test_モデル実行中の権限変更で回答を保留する |
| Given | client, monkeypatch |
| When | client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | result['status'] == 'held' and '絶対に送信' not in result['answer'] |


### TC035

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | モデル呼び出し失敗を失敗件数として区別する |
| test node | backend/tests/test_workflow.py::test_モデル呼び出し失敗を失敗件数として区別する |
| Given | client, monkeypatch |
| When | client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | result['status'] == 'failed' and result['citations'] == [] |


### TC036

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 不正な索引来歴をモデルへ渡さない |
| test node | backend/tests/test_workflow.py::test_不正な索引来歴をモデルへ渡さない |
| Given | client, db |
| When | client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | ask(client).json()['status'] == 'held' ; ask(client).json()['status'] == 'held' |


### TC037

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 失効したジョブは公開版を戻さない |
| test node | backend/tests/test_workflow.py::test_失効したジョブは公開版を戻さない |
| Given | client |
| When | client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{old['id']}", headers=headers('operator')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) |
| Then | client.post(f"/api/operations/jobs/{old['id']}", headers=headers('operator')).json()['status'] == 'obsolete' ; ask(client).json()['citations'][0]['version_id'] == v2['id'] |


### TC038

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 外部索引失敗を記録して部分完了をreadyにしない |
| test node | backend/tests/test_workflow.py::test_外部索引失敗を記録して部分完了をreadyにしない |
| Given | client, monkeypatch |
| When | client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) |
| Then | result['status'] == 'failed' and result['error_code'] == 'external_failure' ; ask(client).json()['status'] == 'held' |


### TC039

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | workerが未配送ジョブを処理する |
| test node | backend/tests/test_workflow.py::test_workerが未配送ジョブを処理する |
| Given | client |
| When | client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) |
| Then | run_once(client.app.state.runtime) == 1 ; run_once(client.app.state.runtime) == 0 ; ask(client).json()['status'] == 'answered' |


### TC040

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 回答根拠の欠落と改変は閲覧時に非表示とする |
| test node | backend/tests/test_workflow.py::test_回答根拠の欠落と改変は閲覧時に非表示とする |
| Given | client, db, target |
| When | client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | result[0]['status'] == 'hidden' and result[0]['citations'] == [] |


### TC041

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 中断した質問は同じIDで再開し二重計上しない |
| test node | backend/tests/test_workflow.py::test_中断した質問は同じIDで再開し二重計上しない |
| Given | client, db |
| When | client.post('/api/chat', headers=headers('reader', key), json=data.model_dump()) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | result.status_code == 200 ; result.json()['conversation_id'] == first.conversation_id ; len([e for e in db.tables['events'].values() if e['kind'] == 'question']) == 1 |


### TC042

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 外部検索は返されたID以外を根拠にしない |
| test node | backend/tests/test_workflow.py::test_外部検索は返されたID以外を根拠にしない |
| Given | client, monkeypatch |
| When | client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | ask(client).json()['status'] == 'held' |


### TC043

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | モデル入力直前に失効を検知した場合はモデルを呼ばない |
| test node | backend/tests/test_workflow.py::test_モデル入力直前に失効を検知した場合はモデルを呼ばない |
| Given | client, monkeypatch |
| When | client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | ask(client).json()['status'] == 'held' |


### TC044

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 削除配送を100行単位で再開し共有本文を残す |
| test node | backend/tests/test_workflow.py::test_削除配送を100行単位で再開し共有本文を残す |
| Given | client, db |
| When | client.get(f"/api/documents/{other['id']}", headers=headers('reader')) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('leader'), json={'revision': current['revision'], 'visibility': 'department', 'shared_departments': [], 'status': 'active', 'reason': '検証文書の利用終了', **kwargs}) ; client.get('/api/documents?scope=manage', headers=headers('leader')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | not [c for c in db.tables['chunks'].values() if c['document_id'] == doc['id']] ; client.get(f"/api/documents/{other['id']}", headers=headers('reader')).status_code == 200 |


### TC045

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | HTTP処理ログを通常のINFO設定で出力し本文とトークンを含めない |
| test node | backend/tests/test_workflow.py::test_HTTP処理ログを通常のINFO設定で出力し本文とトークンを含めない |
| Given | client, caplog |
| When | client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) |
| Then | messages and all(('request_id=' in message for message in messages)) ; 'ログへ出さない' not in ''.join(messages) ; 'demo-author' not in ''.join(messages) |
