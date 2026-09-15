<!-- 実装から生成。直接編集しない。入力SHA256: 065f3a0aaa159ee25b4b54797ae13bebd5e0deb08cdd00f2becc4afbe26e1319 -->

# API一覧

## APIグループ

- [health](api/health/README.md)
- [documents](api/documents/README.md)
- [reviews](api/reviews/README.md)
- [images](api/images/README.md)
- [groups](api/groups/README.md)
- [metrics](api/metrics/README.md)
- [operations](api/operations/README.md)
- [chat](api/chat/README.md)

## API一覧

| method | path | 目的 | 6帳票の入口 |
| --- | --- | --- | --- |
| GET | /api/health | 死活確認 | [health](api/health/health/README.md) |
| POST | /api/documents | 文書を作成 | [create_document](api/documents/create_document/README.md) |
| GET | /api/documents | 閲覧可能な文書を検索 | [list_documents](api/documents/list_documents/README.md) |
| GET | /api/documents/{document_id}/draft | 下書きを取得 | [get_draft](api/documents/get_draft/README.md) |
| PUT | /api/documents/{document_id}/draft | 競合を検出して下書きを保存 | [save_draft](api/documents/save_draft/README.md) |
| POST | /api/documents/{document_id}/submissions | 版を確定して承認申請 | [submit_version](api/documents/submit_version/README.md) |
| GET | /api/documents/{document_id} | 承認版または担当版を表示 | [read_document](api/documents/read_document/README.md) |
| GET | /api/documents/{document_id}/history | 担当文書の版履歴 | [version_history](api/documents/version_history/README.md) |
| GET | /api/documents/{document_id}/diff | 版IDを指定して本文差分を比較 | [version_diff](api/documents/version_diff/README.md) |
| PUT | /api/documents/{document_id}/policy | リーダーが公開範囲・公開停止・削除を管理 | [change_policy](api/documents/change_policy/README.md) |
| GET | /api/reviews | 審査状況を一覧 | [list_reviews](api/reviews/list_reviews/README.md) |
| POST | /api/reviews/{submission_id}/decision | manifestを確認して承認・却下 | [decide_review](api/reviews/decide_review/README.md) |
| POST | /api/images/documents/{document_id} | 画像を添付して位置付きOCRを実行 | [upload_image](api/images/upload_image/README.md) |
| GET | /api/images/{asset_id} | 現在の認可で画像を配信 | [get_image](api/images/get_image/README.md) |
| GET | /api/images/ocr/{run_id} | 認可されたOCR領域を取得 | [get_ocr](api/images/get_ocr/README.md) |
| POST | /api/images/{asset_id}/ocr | OCRを訂正し新しいrunを保存 | [correct_ocr](api/images/correct_ocr/README.md) |
| GET | /api/groups/me | 本人と現在の所属権限を取得 | [get_identity](api/groups/get_identity/README.md) |
| GET | /api/groups/{department_id}/members | 自部署の所属を一覧 | [list_members](api/groups/list_members/README.md) |
| PUT | /api/groups/memberships | 部署の所属権限を変更 | [change_membership](api/groups/change_membership/README.md) |
| POST | /api/metrics/views/{document_id} | 実閲覧を一意IDで記録 | [record_view](api/metrics/record_view/README.md) |
| GET | /api/metrics/{department_id} | 部署の利用数と文書貢献を集計 | [department_metrics](api/metrics/department_metrics/README.md) |
| POST | /api/operations/jobs/{job_id} | 反映ジョブを再処理 | [retry_job](api/operations/retry_job/README.md) |
| GET | /api/operations/jobs | 反映ジョブと失敗理由を確認 | [list_jobs](api/operations/list_jobs/README.md) |
| GET | /api/operations/reconcile | 正本と索引の不一致を確認 | [reconcile_index](api/operations/reconcile_index/README.md) |
| POST | /api/chat | 最新承認版の根拠で回答 | [ask_question](api/chat/ask_question/README.md) |
| GET | /api/chat/{conversation_id} | 現行認可で会話履歴を再表示 | [chat_history](api/chat/chat_history/README.md) |
