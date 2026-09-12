<!-- 実装から生成。直接編集しない。入力SHA256: 31de213f242d3d7bf0d4f5957d4ef327aaacb2267a973d8e0adce1f1531ac7e1 -->

# 最新承認版の根拠で回答 — 単体テスト詳細

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

対象: `backend/src/kotorelay/context.py:70`。式: `doc.status != 'active' or not self.memberships`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F03-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F03-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F04 条件分岐

対象: `backend/src/kotorelay/context.py:72`。式: `doc.visibility == 'organization'`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F04-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F04-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F05 条件分岐

対象: `backend/src/kotorelay/context.py:74`。式: `self.member(doc.department_id)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F05-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F05-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F06 条件分岐

対象: `backend/src/kotorelay/context.py:53`。式: `q.organizations_fence(self.db, self.organization) == 1`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F06-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F06-false | 不成立 | 'conflict' / 409 |


### F07 条件分岐

対象: `backend/src/kotorelay/context.py:129`。式: `not rows`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F07-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F07-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F08 条件分岐

対象: `backend/src/kotorelay/context.py:132`。式: `record.operation == operation and record.request_hash == digest(request.encode())`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F08-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F08-false | 不成立 | 'idempotency_conflict' / 409 |


### F09 条件分岐

対象: `backend/src/kotorelay/errors.py:13`。式: `not condition`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F09-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F09-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F10 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:217`。式: `ctx.member(prepared.department_id)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F10-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F10-false | 不成立 | 'forbidden' / 403 |


### F11 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:78`。式: `prior`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F11-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F11-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F12 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:103`。式: `resumed is not None`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F12-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F12-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F13 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:186`。式: `resumed is None`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F13-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F13-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F14 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:75`。式: `ctx.member(data.department_id)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F14-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F14-false | 不成立 | 'forbidden' / 403 |


### F15 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:92`。式: `resumed is not None or sum((1 for e in events if e.user_id == ctx.user.id and e.kind == 'question' and (e.created_at.date() == today))) < ctx.settings.max_questions_per_day`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F15-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F15-false | 不成立 | 'limit' / 429 |


### F16 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:105`。式: `data.conversation_id`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F16-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F16-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F17 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:134`。式: `chunk.document_id not in docs or chunk.version_id != docs[chunk.document_id].latest_version_id or (not chunk.ready)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F17-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F17-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F18 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:140`。式: `vector_keys is not None and chunk.id not in vector_keys`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F18-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F18-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F19 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:151`。式: `score > 0 and (vector_keys is not None or score >= max(1, len(terms(data.question)) * 0.3))`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F19-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F19-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F20 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:173`。式: `not validate_citation(ctx, citation)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F20-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F20-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F21 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:177`。式: `len(images) + len(related) > ctx.settings.max_model_images`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F21-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F21-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F22 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:184`。式: `len(citations) >= 5`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F22-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F22-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F23 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:79`。式: `prior[0].user_id == ctx.user.id and ctx.objects.get(prior[0].question_key).decode() == data.question and (prior[0].department_id == data.department_id) and (data.conversation_id is None or data.conversation_id == prior[0].conversation_id)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F23-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F23-false | 不成立 | 'idempotency_conflict' / 409 |


### F24 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:107`。式: `bool(conversations) and conversations[0].user_id == ctx.user.id`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F24-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F24-false | 不成立 | not_found / 404 |


### F25 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:109`。式: `all((a.department_id == data.department_id for a in q.answers_list(ctx.db, ctx.org) if a.conversation_id == conversation_id))`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F25-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F25-false | 不成立 | 'conversation_department' / 409 |


### F26 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:275`。式: `answer.user_id == ctx.user.id`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F26-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F26-false | 不成立 | not_found / 404 |


### F27 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:30`。式: `not docs`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F27-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F27-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F28 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:33`。式: `not ctx.can_read(doc) or doc.latest_version_id != citation.version_id or doc.revision != citation.document_revision`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F28-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F28-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F29 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:41`。式: `not versions or not chunks`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F29-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F29-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F30 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:44`。式: `not (digest(version.manifest.encode()) == version.manifest_hash and version.document_id == doc.id and chunk.ready and (chunk.version_id == version.id) and (chunk.document_id == doc.id) and (chunk.manifest_hash == version.manifest_hash == citation.manifest_hash) and (chunk.sha256 == citation.chunk_hash))`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F30-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F30-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F31 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:59`。式: `placements - {image.placement.id for image in manifest.images}`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F31-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F31-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F32 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:62`。式: `image.placement.id in json.loads(chunk.placements)`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F32-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F32-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F33 条件分岐

対象: `backend/src/kotorelay/operations/chat/functions.py:65`。式: `not assets or not runs or (not runs[0].confirmed) or (runs[0].status != 'ready')`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F33-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F33-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F34 条件分岐

対象: `backend/src/kotorelay/operations/chat/service.py:23`。式: `prepared.citations`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F34-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F34-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F35 条件分岐

対象: `backend/src/kotorelay/operations/chat/service.py:28`。式: `prepared.citations`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F35-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F35-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F36 条件分岐

対象: `backend/src/kotorelay/operations/chat/service.py:17`。式: `exc.code != 'already_answered'`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F36-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F36-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


### F37 条件分岐

対象: `backend/src/kotorelay/operations/chat/service.py:26`。式: `not all((f.validate_citation(ctx, c) for c in prepared.citations))`

| 要素ID | 要素 | 期待観点 |
| --- | --- | --- |
| F37-true | 成立 | 成立側の実装を実行。正常／異常は上記式と処理に依存する。 |
| F37-false | 不成立 | then / else の実装分岐 / 制御フロー参照 |


## 2. 直積したテストケース一覧

参照先と同じ章名を保持しています。ここでは実在するテストを列挙します。要因の完全な直積や到達不能条件の自動証明は実装していないため、全組合せの網羅を示す表ではありません。API群に共通する境界試験を含みます。

| Case ID | 日本語ケース | test node |
| --- | --- | --- |
| TC001 | 未承認文書は閲覧と検索へ現れない | backend/tests/test_workflow.py::test_未承認文書は閲覧と検索へ現れない |
| TC002 | 承認された版だけを引用付きで回答する | backend/tests/test_workflow.py::test_承認された版だけを引用付きで回答する |
| TC003 | 新しい下書きは公開タイトルと本文を変更しない | backend/tests/test_workflow.py::test_新しい下書きは公開タイトルと本文を変更しない |
| TC004 | 新版承認後の未反映期間は旧版を使わない | backend/tests/test_workflow.py::test_新版承認後の未反映期間は旧版を使わない |
| TC005 | 公開停止と削除で回答履歴も失効する | backend/tests/test_workflow.py::test_公開停止と削除で回答履歴も失効する |
| TC006 | 他部署は直接IDと一覧とRAGから取得できない | backend/tests/test_workflow.py::test_他部署は直接IDと一覧とRAGから取得できない |
| TC007 | 所属停止は古いトークンでも即時反映する | backend/tests/test_workflow.py::test_所属停止は古いトークンでも即時反映する |
| TC008 | 閲覧と質問の再送を重複計上しない | backend/tests/test_workflow.py::test_閲覧と質問の再送を重複計上しない |
| TC009 | 他人の会話と管理統計を拒否する | backend/tests/test_workflow.py::test_他人の会話と管理統計を拒否する |
| TC010 | 画像のOCR確認をmanifestへ固定する | backend/tests/test_workflow.py::test_画像のOCR確認をmanifestへ固定する |
| TC011 | 反映失敗を照合し再試行で回復する | backend/tests/test_workflow.py::test_反映失敗を照合し再試行で回復する |
| TC012 | 画像を含む削除を保持期間後に完了する | backend/tests/test_workflow.py::test_画像を含む削除を保持期間後に完了する |
| TC013 | モデル実行中の権限変更で回答を保留する | backend/tests/test_workflow.py::test_モデル実行中の権限変更で回答を保留する |
| TC014 | モデル呼び出し失敗を失敗件数として区別する | backend/tests/test_workflow.py::test_モデル呼び出し失敗を失敗件数として区別する |
| TC015 | 不正な索引来歴をモデルへ渡さない | backend/tests/test_workflow.py::test_不正な索引来歴をモデルへ渡さない |
| TC016 | 利用上限を超えた質問を受け付けない | backend/tests/test_workflow.py::test_利用上限を超えた質問を受け付けない |
| TC017 | 失効したジョブは公開版を戻さない | backend/tests/test_workflow.py::test_失効したジョブは公開版を戻さない |
| TC018 | 外部索引失敗を記録して部分完了をreadyにしない | backend/tests/test_workflow.py::test_外部索引失敗を記録して部分完了をreadyにしない |
| TC019 | workerが未配送ジョブを処理する | backend/tests/test_workflow.py::test_workerが未配送ジョブを処理する |
| TC020 | 回答根拠の欠落と改変は閲覧時に非表示とする | backend/tests/test_workflow.py::test_回答根拠の欠落と改変は閲覧時に非表示とする |
| TC021 | 中断した質問は同じIDで再開し二重計上しない | backend/tests/test_workflow.py::test_中断した質問は同じIDで再開し二重計上しない |
| TC022 | 外部検索は返されたID以外を根拠にしない | backend/tests/test_workflow.py::test_外部検索は返されたID以外を根拠にしない |
| TC023 | モデル入力直前に失効を検知した場合はモデルを呼ばない | backend/tests/test_workflow.py::test_モデル入力直前に失効を検知した場合はモデルを呼ばない |


## 3. テスト詳細

### TC001

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 未承認文書は閲覧と検索へ現れない |
| test node | backend/tests/test_workflow.py::test_未承認文書は閲覧と検索へ現れない |
| Given | client |
| When | client.get(f"/api/documents/{doc['id']}", headers=headers('reader')) ; client.get('/api/documents', headers=headers('reader')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) |
| Then | client.get('/api/documents', headers=headers('reader')).json() == [] ; client.get(f"/api/documents/{doc['id']}", headers=headers('reader')).status_code == 404 ; result['status'] == 'held' and result['citations'] == [] |


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
| 日本語ケース | 所属停止は古いトークンでも即時反映する |
| test node | backend/tests/test_workflow.py::test_所属停止は古いトークンでも即時反映する |
| Given | client |
| When | client.put('/api/groups/memberships', headers=headers('leader'), json={'user_id': stable_id('reader'), 'department_id': DEPT, 'active': False}) ; client.get(f"/api/documents/{doc['id']}", headers=headers('reader')) ; client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | response.status_code == 200 ; client.get(f"/api/documents/{doc['id']}", headers=headers('reader')).status_code == 404 ; client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')).json()[0]['status'] == 'hidden' |


### TC008

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 閲覧と質問の再送を重複計上しない |
| test node | backend/tests/test_workflow.py::test_閲覧と質問の再送を重複計上しない |
| Given | client |
| When | client.post('/api/chat', headers=headers('reader', key), json=question) ; client.post('/api/chat', headers=headers('reader', key), json=question) ; client.get(f'/api/metrics/{DEPT}?start=2020-01-01T00:00:00Z&end=2100-01-01T00:00:00Z', headers=headers('leader')) ; client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view) ; client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view).json()['recorded'] ; not client.post(f"/api/metrics/views/{doc['id']}", headers=headers('reader'), json=view).json()['recorded'] ; a.json() == b.json() ; metrics['questions'] == 1 and metrics['views'] == 1 and (metrics['unique_viewers'] == 1) ; metrics['documents'][0]['contributions'] == 1 ; 'question' not in str(metrics['documents']) |


### TC009

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 他人の会話と管理統計を拒否する |
| test node | backend/tests/test_workflow.py::test_他人の会話と管理統計を拒否する |
| Given | client |
| When | client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('leader')) ; client.get(f'/api/metrics/{DEPT}?start=2020-01-01T00:00:00Z&end=2100-01-01T00:00:00Z', headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('leader')).status_code == 404 ; ask(client, 'author', conversation_id=answer['conversation_id']).status_code == 404 ; client.get(f'/api/metrics/{DEPT}?start=2020-01-01T00:00:00Z&end=2100-01-01T00:00:00Z', headers=headers('reader')).status_code == 403 |


### TC010

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 画像のOCR確認をmanifestへ固定する |
| test node | backend/tests/test_workflow.py::test_画像のOCR確認をmanifestへ固定する |
| Given | client |
| When | client.post(f"/api/images/documents/{doc['id']}", headers=headers(), files={'file': ('image.png', buf.getvalue(), 'image/png')}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '画像手順', 'body': '画像の開発フロー', 'revision': 2, 'placements': [p]}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': '画像手順', 'body': '画像の開発フロー', 'revision': 3, 'placements': [p]}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': 3}) ; client.post(f"/api/images/{asset['id']}/ocr", headers=headers(), json={'regions': [{'text': '承認後に開発を開始', 'x': 0, 'y': 0, 'width': 1, 'height': 1, 'confidence': 1, 'order': 0}], 'confirmed': True}) ; client.get(f"/api/images/{asset['id']}?version_id={version['id']}", headers=headers('reader')) ; client.get(f"/api/images/{asset['id']}", headers=headers('reader')) ; client.get(f"/api/images/ocr/{run['id']}?version_id={version['id']}", headers=headers('reader')) ; client.get(f"/api/images/ocr/{p['ocr_run_id']}", headers=headers()) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('leader'), json={'revision': current['revision'], 'visibility': 'department', 'shared_departments': [], 'status': 'active', 'reason': '検証文書の利用終了', **kwargs}) ; client.get('/api/documents?scope=manage', headers=headers('leader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) |
| Then | upload.status_code == 201 ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': 3}).status_code == 409 ; client.get(f"/api/images/{asset['id']}?version_id={version['id']}", headers=headers('reader')).status_code == 200 ; client.get(f"/api/images/{asset['id']}", headers=headers('reader')).status_code == 404 ; client.get(f"/api/images/ocr/{run['id']}?version_id={version['id']}", headers=headers('reader')).status_code == 404 ; ask(client).json()['status'] == 'answered' ; client.get(f"/api/images/ocr/{p['ocr_run_id']}", headers=headers()).status_code == 200 ; ask(client).status_code == 200 ; ask(client).status_code == 200 |


### TC011

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 反映失敗を照合し再試行で回復する |
| test node | backend/tests/test_workflow.py::test_反映失敗を照合し再試行で回復する |
| Given | client, monkeypatch |
| When | client.get('/api/operations/reconcile', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.get('/api/operations/reconcile', headers=headers('operator')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('leader'), json={'revision': current['revision'], 'visibility': 'department', 'shared_departments': [], 'status': 'active', 'reason': '検証文書の利用終了', **kwargs}) ; client.get('/api/documents?scope=manage', headers=headers('leader')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) |
| Then | differences[0]['reason'] == '最新承認版が未反映' ; result['status'] == 'failed' ; ask(client).json()['status'] == 'held' ; result['status'] == 'done' ; ask(client).json()['status'] == 'answered' ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')).json()['attempts'] == 2 ; '停止済み' in client.get('/api/operations/reconcile', headers=headers('operator')).json()[0]['reason'] |


### TC012

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 画像を含む削除を保持期間後に完了する |
| test node | backend/tests/test_workflow.py::test_画像を含む削除を保持期間後に完了する |
| Given | client, db |
| When | client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(url, headers=headers('operator')) ; client.post(url, headers=headers('operator')) ; client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.put(f"/api/documents/{doc['id']}/policy", headers=headers('leader'), json={'revision': current['revision'], 'visibility': 'department', 'shared_departments': [], 'status': 'active', 'reason': '検証文書の利用終了', **kwargs}) ; client.get('/api/documents?scope=manage', headers=headers('leader')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | policy(client, doc, status='deleted').status_code == 200 ; client.post(url, headers=headers('operator')).json()['status'] == 'retained' ; client.post(url, headers=headers('operator')).json()['status'] == 'done' ; not any((c['document_id'] == doc['id'] for c in db.tables['chunks'].values())) ; not any((d['document_id'] == doc['id'] for d in db.tables['drafts'].values())) ; client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')).json()[0]['status'] == 'hidden' |


### TC013

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | モデル実行中の権限変更で回答を保留する |
| test node | backend/tests/test_workflow.py::test_モデル実行中の権限変更で回答を保留する |
| Given | client, monkeypatch |
| When | client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | result['status'] == 'held' and '絶対に送信' not in result['answer'] |


### TC014

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | モデル呼び出し失敗を失敗件数として区別する |
| test node | backend/tests/test_workflow.py::test_モデル呼び出し失敗を失敗件数として区別する |
| Given | client, monkeypatch |
| When | client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | result['status'] == 'failed' and result['citations'] == [] |


### TC015

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 不正な索引来歴をモデルへ渡さない |
| test node | backend/tests/test_workflow.py::test_不正な索引来歴をモデルへ渡さない |
| Given | client, db |
| When | client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | ask(client).json()['status'] == 'held' ; ask(client).json()['status'] == 'held' |


### TC016

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 利用上限を超えた質問を受け付けない |
| test node | backend/tests/test_workflow.py::test_利用上限を超えた質問を受け付けない |
| Given | client |
| When | client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) |
| Then | ask(client).status_code == 200 ; ask(client).status_code == 429 |


### TC017

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 失効したジョブは公開版を戻さない |
| test node | backend/tests/test_workflow.py::test_失効したジョブは公開版を戻さない |
| Given | client |
| When | client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{old['id']}", headers=headers('operator')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) |
| Then | client.post(f"/api/operations/jobs/{old['id']}", headers=headers('operator')).json()['status'] == 'obsolete' ; ask(client).json()['citations'][0]['version_id'] == v2['id'] |


### TC018

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 外部索引失敗を記録して部分完了をreadyにしない |
| test node | backend/tests/test_workflow.py::test_外部索引失敗を記録して部分完了をreadyにしない |
| Given | client, monkeypatch |
| When | client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) |
| Then | result['status'] == 'failed' and result['error_code'] == 'external_failure' ; ask(client).json()['status'] == 'held' |


### TC019

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | workerが未配送ジョブを処理する |
| test node | backend/tests/test_workflow.py::test_workerが未配送ジョブを処理する |
| Given | client |
| When | client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) |
| Then | run_once(client.app.state.runtime) == 1 ; run_once(client.app.state.runtime) == 0 ; ask(client).json()['status'] == 'answered' |


### TC020

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 回答根拠の欠落と改変は閲覧時に非表示とする |
| test node | backend/tests/test_workflow.py::test_回答根拠の欠落と改変は閲覧時に非表示とする |
| Given | client, db, target |
| When | client.get(f"/api/chat/{answer['conversation_id']}", headers=headers('reader')) ; client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | result[0]['status'] == 'hidden' and result[0]['citations'] == [] |


### TC021

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 中断した質問は同じIDで再開し二重計上しない |
| test node | backend/tests/test_workflow.py::test_中断した質問は同じIDで再開し二重計上しない |
| Given | client, db |
| When | client.post('/api/chat', headers=headers('reader', key), json=data.model_dump()) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | result.status_code == 200 ; result.json()['conversation_id'] == first.conversation_id ; len([e for e in db.tables['events'].values() if e['kind'] == 'question']) == 1 |


### TC022

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | 外部検索は返されたID以外を根拠にしない |
| test node | backend/tests/test_workflow.py::test_外部検索は返されたID以外を根拠にしない |
| Given | client, monkeypatch |
| When | client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | ask(client).json()['status'] == 'held' |


### TC023

| 項目 | 内容 |
| --- | --- |
| 日本語ケース | モデル入力直前に失効を検知した場合はモデルを呼ばない |
| test node | backend/tests/test_workflow.py::test_モデル入力直前に失効を検知した場合はモデルを呼ばない |
| Given | client, monkeypatch |
| When | client.post('/api/chat', headers=headers(persona), json={'question': '開発フローの承認を教えて', 'department_id': DEPT, **kwargs}) ; client.post('/api/documents', headers=headers(), json={'title': '開発ガイド', 'department_id': DEPT}) ; client.put(f"/api/documents/{doc['id']}/draft", headers=headers(), json={'title': doc['title'], 'body': body, 'revision': 1}) ; client.post(f"/api/documents/{doc['id']}/submissions", headers=headers(), json={'revision': revision}) ; client.get(f"/api/documents/{doc['id']}/draft", headers=headers()) ; client.post(f"/api/reviews/{review['id']}/decision", headers=headers('reviewer'), json={'decision': decision, 'reason': reason, 'manifest_hash': version['manifest_hash']}) ; client.get('/api/reviews', headers=headers('reviewer')) ; client.get('/api/operations/jobs', headers=headers('operator')) ; client.post(f"/api/operations/jobs/{job['id']}", headers=headers('operator')) |
| Then | ask(client).json()['status'] == 'held' |
