<!-- 実装から生成。直接編集しない。入力SHA256: 987c18a693c5fa5c9f59f732c65771f1c047c0829e22a5d72b689276aae93c56 -->

# 認可されたOCR領域を取得 — 単体テスト詳細

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

対象: `backend/src/kotorelay/context.py:71`。式: `doc.status != 'active' or not self.memberships`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F03-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F03-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F04 条件分岐

対象: `backend/src/kotorelay/context.py:73`。式: `doc.visibility == 'organization'`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F04-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F04-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F05 条件分岐

対象: `backend/src/kotorelay/context.py:75`。式: `self.member(doc.department_id)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F05-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F05-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F06 条件分岐

対象: `backend/src/kotorelay/context.py:83`。式: `bool(rows)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F06-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F06-false | 不成立 | not_found / 404 |


### F07 条件分岐

対象: `backend/src/kotorelay/context.py:90`。式: `allowed`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F07-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F07-false | 不成立 | not_found / 404 |


### F08 条件分岐

対象: `backend/src/kotorelay/context.py:61`。式: `m.department_id == department_id`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F08-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F08-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F09 条件分岐

対象: `backend/src/kotorelay/context.py:97`。式: `not self.permission(doc.department_id, 'draft')`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F09-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F09-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F10 条件分岐

対象: `backend/src/kotorelay/context.py:95`。式: `bool(rows) and rows[0].document_id == doc.id`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F10-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F10-false | 不成立 | not_found / 404 |


### F11 条件分岐

対象: `backend/src/kotorelay/context.py:99`。式: `digest(version.manifest.encode()) == version.manifest_hash`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F11-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F11-false | 不成立 | 'integrity' / 503 |


### F12 条件分岐

対象: `backend/src/kotorelay/context.py:98`。式: `self.can_read(doc) and doc.latest_version_id == version.id`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F12-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F12-false | 不成立 | not_found / 404 |


### F13 条件分岐

対象: `backend/src/kotorelay/errors.py:13`。式: `not condition`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F13-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F13-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F14 条件分岐

対象: `backend/src/kotorelay/operations/images/get_ocr/functions.py:17`。式: `version_id`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F14-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F14-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F15 条件分岐

対象: `backend/src/kotorelay/operations/images/get_ocr/functions.py:14`。式: `bool(rows)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F15-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F15-false | 不成立 | not_found / 404 |


### F16 条件分岐

対象: `backend/src/kotorelay/operations/images/get_ocr/functions.py:20`。式: `any((i.placement.ocr_run_id == run.id and i.ocr_hash == run.result_hash for i in Manifest.model_validate_json(version.manifest).images))`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F16-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F16-false | 不成立 | not_found / 404 |


### F17 条件分岐

対象: `backend/src/kotorelay/operations/images/shared/functions.py:16`。式: `version_id is None`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F17-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F17-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F18 条件分岐

対象: `backend/src/kotorelay/operations/images/shared/functions.py:14`。式: `bool(assets)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F18-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F18-false | 不成立 | not_found / 404 |


### F19 条件分岐

対象: `backend/src/kotorelay/operations/images/shared/functions.py:20`。式: `bool(docs) and docs[0].status != 'deleted'`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F19-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F19-false | 不成立 | not_found / 404 |


### F20 条件分岐

対象: `backend/src/kotorelay/operations/images/shared/functions.py:22`。式: `ctx.can_read(doc) or ctx.permission(doc.department_id, 'draft')`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F20-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F20-false | 不成立 | not_found / 404 |


### F21 条件分岐

対象: `backend/src/kotorelay/operations/images/shared/functions.py:25`。式: `any((i.placement.asset_id == asset.id and i.image_hash == asset.sha256 for i in manifest.images))`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F21-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F21-false | 不成立 | not_found / 404 |


## 2. 直積したテストケース一覧

参照先と同じ章名を保持しています。ここでは実在するテストを列挙します。要因の完全な直積や到達不能条件の自動証明は実装していないため、全組合せの網羅を示す表ではありません。API群に共通する境界試験を含みます。

| Case ID | 日本語ケース | test node |
| --- | --- | --- |
| TC001 | OCR領域の複数行訂正と削除追加でも識別座標を保つ | backend/tests/test_ui_contract.py::test_OCR領域の複数行訂正と削除追加でも識別座標を保つ |
| TC002 | 旧OCRの読取は安定IDを補うだけで保存済みハッシュを変えない | backend/tests/test_ui_contract.py::test_旧OCRの読取は安定IDを補うだけで保存済みハッシュを変えない |
| TC003 | 代替テキストと絵文字位置を承認版へ固定する | backend/tests/test_ui_contract.py::test_代替テキストと絵文字位置を承認版へ固定する |
| TC004 | 画像のOCR確認をmanifestへ固定する | backend/tests/test_workflow.py::test_画像のOCR確認をmanifestへ固定する |
| TC005 | 不正画像を拒否する | backend/tests/test_workflow.py::test_不正画像を拒否する |


## 3. テスト詳細

### TC001

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | OCR領域の複数行訂正と削除追加でも識別座標を保つ |
| test node | backend/tests/test_ui_contract.py::test_OCR領域の複数行訂正と削除追加でも識別座標を保つ |
| Given | client |
| When | client.post(f"/api/images/{asset['id']}/ocr", headers=headers(), json={'regions': [regions[0], regions[0]], 'confirmed': True}) ; client.post(f"/api/images/{asset['id']}/ocr", headers=headers(), json={'regions': values, 'confirmed': True}) ; client.get(f"/api/images/ocr/{first['ocr_run']['id']}", headers=headers()) ; client.post(f"/api/images/documents/{doc['id']}", headers=headers(), files={'file': ('x.png', buf.getvalue(), 'image/png')}) |
| Then | value['region_id'] == ids[1] and value['x'] == 0.3 and (value['text'] == '複数行\n訂正内容') ; value['confidence'] is None and value['source'] == 'human' ; before['regions'][0]['text'] == '0' and before['confirmed'] is True ; duplicate.status_code == 422 ; response.status_code == 200 |


### TC002

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 旧OCRの読取は安定IDを補うだけで保存済みハッシュを変えない |
| test node | backend/tests/test_ui_contract.py::test_旧OCRの読取は安定IDを補うだけで保存済みハッシュを変えない |
| Given | client, db |
| When | client.get(f'/api/images/ocr/{rid}', headers=headers()) ; client.get(f'/api/images/ocr/{rid}', headers=headers()) ; client.post(f"/api/images/documents/{doc['id']}", headers=headers(), files={'file': ('x.png', buf.getvalue(), 'image/png')}) |
| Then | first['regions'][0]['region_id'] == second['regions'][0]['region_id'] ; q.ocr_runs_get(ctx.db, ctx.org, rid)[0].result_hash == key ; json.loads(ctx.objects.get(key)) == value |


### TC003

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 代替テキストと絵文字位置を承認版へ固定する |
| test node | backend/tests/test_ui_contract.py::test_代替テキストと絵文字位置を承認版へ固定する |
| Given | client |
| When | client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '画像手順', 'body': '日😀本文', 'revision': 2, 'placements': [placement]}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '次版', 'body': '日😀本文', 'revision': 3, 'placements': [placement]}) ; client.get(f"/api/documents/{doc['id']}", headers=headers('reader')) ; client.post(f"/api/images/{data['asset']['id']}/ocr", headers=headers(), json={'regions': [], 'confirmed': True}) ; client.post(f"/api/images/documents/{doc['id']}", headers=headers(), files={'file': ('x.png', buf.getvalue(), 'image/png')}) |
| Then | saved.status_code == 200 ; json.loads(version['manifest'])['images'][0]['placement'] == placement ; json.loads(old['version']['manifest'])['images'][0]['placement']['alt_text'] == '受付から承認へ進む図' |


### TC004

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 画像のOCR確認をmanifestへ固定する |
| test node | backend/tests/test_workflow.py::test_画像のOCR確認をmanifestへ固定する |
| Given | client |
| When | client.post(f"/api/images/documents/{doc['id']}", headers=headers(), files={'file': ('image.png', buf.getvalue(), 'image/png')}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '画像手順', 'body': '画像の開発フロー', 'revision': 2, 'placements': [p]}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '画像手順', 'body': '画像の開発フロー', 'revision': 3, 'placements': [p]}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': 3}) ; client.post(f"/api/images/{asset['id']}/ocr", headers=headers(), json={'regions': [{'text': '承認後に開発を開始', 'x': 0, 'y': 0, 'width': 1, 'height': 1, 'confidence': 1, 'order': 0}], 'confirmed': True}) ; client.get(f"/api/images/{asset['id']}?version_id={version['id']}", headers=headers('reader')) ; client.get(f"/api/images/{asset['id']}", headers=headers('reader')) ; client.get(f"/api/images/ocr/{run['id']}?version_id={version['id']}", headers=headers('reader')) ; client.get(f"/api/images/ocr/{p['ocr_run_id']}", headers=headers()) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('leader'), json={'revision': current['revision'], 'visibility': 'department', 'shared_departments': [], 'status': 'active', 'reason': '検証文書の利用終了', **kwargs}) ; client.get('/api/documents?scope=manage', headers=headers('leader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) |
| Then | upload.status_code == 201 ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': 3}).status_code == 409 ; client.get(f"/api/images/{asset['id']}?version_id={version['id']}", headers=headers('reader')).status_code == 200 ; client.get(f"/api/images/{asset['id']}", headers=headers('reader')).status_code == 404 ; client.get(f"/api/images/ocr/{run['id']}?version_id={version['id']}", headers=headers('reader')).status_code == 404 ; ask(client).json()['status'] == 'answered' ; client.get(f"/api/images/ocr/{p['ocr_run_id']}", headers=headers()).status_code == 200 ; ask(client).status_code == 200 ; ask(client).status_code == 200 |


### TC005

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 不正画像を拒否する |
| test node | backend/tests/test_workflow.py::test_不正画像を拒否する |
| Given | client, payload |
| When | client.post(f"/api/images/documents/{doc['id']}", headers=headers(), files={'file': ('bad.png', payload, 'image/png')}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) |
| Then | client.post(f"/api/images/documents/{doc['id']}", headers=headers(), files={'file': ('bad.png', payload, 'image/png')}).status_code == 422 |
