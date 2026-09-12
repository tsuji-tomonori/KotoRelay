<!-- 実装から生成。直接編集しない。入力SHA256: e3cb305ddf380bd9917bab7f5404c8ac54c8511b8d91b58e7192aa0d5991c3cf -->

# 認可されたOCR領域を取得 — unit-test

実在するpytest関数とassertから抽出。パラメータごとの実行成否は品質ポータルで確認します。共有するAPI群の境界試験も含みます。

## 入力・認可・分岐要因

| 場所 | 要因／要素 | 異常結果 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:40 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:43 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:70 | doc.status != 'active' or not self.memberships | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:72 | doc.visibility == 'organization' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:74 | self.member(doc.department_id) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:82 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/context.py:89 | allowed | not_found | 404 |
| backend/src/kotorelay/context.py:60 | m.department_id == department_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:96 | not self.permission(doc.department_id, 'draft') | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:94 | bool(rows) and rows[0].document_id == doc.id | not_found | 404 |
| backend/src/kotorelay/context.py:98 | digest(version.manifest.encode()) == version.manifest_hash | 'integrity' | 503 |
| backend/src/kotorelay/context.py:97 | self.can_read(doc) and doc.latest_version_id == version.id | not_found | 404 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/images/functions.py:146 | version_id is None | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/images/functions.py:144 | bool(assets) | not_found | 404 |
| backend/src/kotorelay/operations/images/functions.py:150 | bool(docs) and docs[0].status != 'deleted' | not_found | 404 |
| backend/src/kotorelay/operations/images/functions.py:152 | ctx.can_read(doc) or ctx.permission(doc.department_id, 'draft') | not_found | 404 |
| backend/src/kotorelay/operations/images/functions.py:155 | any((i.placement.asset_id == asset.id and i.image_hash == asset.sha256 for i in manifest.images)) | not_found | 404 |
| backend/src/kotorelay/operations/images/functions.py:174 | version_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/images/functions.py:171 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/operations/images/functions.py:177 | any((i.placement.ocr_run_id == run.id and i.ocr_hash == run.result_hash for i in Manifest.model_validate_json(version.manifest).images)) | not_found | 404 |

## Given / When / Then

| 日本語ケース／test node | Given | When | Then（期待状態） |
| --- | --- | --- | --- |
| 画像のOCR確認をmanifestへ固定する / backend/tests/test_workflow.py::test_画像のOCR確認をmanifestへ固定する | client | client.post(f"/api/images/documents/{doc['id']}", headers=headers(), files={'file': ('image.png', buf.getvalue(), 'image/png')}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '画像手順', 'body': '画像の開発フロー', 'revision': 2, 'placements': [p]}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '画像手順', 'body': '画像の開発フロー', 'revision': 3, 'placements': [p]}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': 3}) ; client.post(f"/api/images/{asset['id']}/ocr", headers=headers(), json={'regions': [{'text': '承認後に開発を開始', 'x': 0, 'y': 0, 'width': 1, 'height': 1, 'confidence': 1, 'order': 0}], 'confirmed': True}) ; client.get(f"/api/images/{asset['id']}?version_id={version['id']}", headers=headers('reader')) ; client.get(f"/api/images/{asset['id']}", headers=headers('reader')) ; client.get(f"/api/images/ocr/{run['id']}?version_id={version['id']}", headers=headers('reader')) ; client.get(f"/api/images/ocr/{p['ocr_run_id']}", headers=headers()) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('leader'), json={'revision': current['revision'], 'visibility': 'department', 'shared_departments': [], 'status': 'active', **kwargs}) ; client.get('/api/documents?scope=manage', headers=headers('leader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) | upload.status_code == 201 ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': 3}).status_code == 409 ; client.get(f"/api/images/{asset['id']}?version_id={version['id']}", headers=headers('reader')).status_code == 200 ; client.get(f"/api/images/{asset['id']}", headers=headers('reader')).status_code == 404 ; client.get(f"/api/images/ocr/{run['id']}?version_id={version['id']}", headers=headers('reader')).status_code == 404 ; ask(client).json()['status'] == 'answered' ; client.get(f"/api/images/ocr/{p['ocr_run_id']}", headers=headers()).status_code == 200 ; ask(client).status_code == 200 ; ask(client).status_code == 200 |
| 不正画像を拒否する / backend/tests/test_workflow.py::test_不正画像を拒否する | client, payload | client.post(f"/api/images/documents/{doc['id']}", headers=headers(), files={'file': ('bad.png', payload, 'image/png')}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) | client.post(f"/api/images/documents/{doc['id']}", headers=headers(), files={'file': ('bad.png', payload, 'image/png')}).status_code == 422 |
