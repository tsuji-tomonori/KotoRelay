<!-- 実装から生成。直接編集しない。入力SHA256: e3cb305ddf380bd9917bab7f5404c8ac54c8511b8d91b58e7192aa0d5991c3cf -->

# API一覧

| method | path | 目的 | 6帳票の入口 |
| --- | --- | --- | --- |
| GET | /api/health | 死活確認 | [health](api/health.detail-design.md) |
| GET | /api/documents | 閲覧可能な文書を検索 | [list_documents](api/list_documents.detail-design.md) |
| POST | /api/documents | 文書を作成 | [create_document](api/create_document.detail-design.md) |
| GET | /api/documents/{document_id}/draft | 下書きを取得 | [get_draft](api/get_draft.detail-design.md) |
| PUT | /api/documents/{document_id}/draft | 競合を検出して下書きを保存 | [save_draft](api/save_draft.detail-design.md) |
| POST | /api/documents/{document_id}/submissions | 版を確定して承認申請 | [submit_version](api/submit_version.detail-design.md) |
| GET | /api/documents/{document_id} | 承認版または担当版を表示 | [read_document](api/read_document.detail-design.md) |
| GET | /api/documents/{document_id}/history | 担当文書の版履歴 | [version_history](api/version_history.detail-design.md) |
| GET | /api/documents/{document_id}/diff | 版IDを指定して本文差分を比較 | [version_diff](api/version_diff.detail-design.md) |
| PUT | /api/documents/{document_id}/policy | リーダーが公開範囲・公開停止・削除を管理 | [change_policy](api/change_policy.detail-design.md) |
| GET | /api/reviews | 審査状況を一覧 | [list_reviews](api/list_reviews.detail-design.md) |
| POST | /api/reviews/{submission_id}/decision | manifestを確認して承認・却下 | [decide_review](api/decide_review.detail-design.md) |
| POST | /api/images/documents/{document_id} | 画像を添付して位置付きOCRを実行 | [upload_image](api/upload_image.detail-design.md) |
| GET | /api/images/{asset_id} | 現在の認可で画像を配信 | [get_image](api/get_image.detail-design.md) |
| POST | /api/images/{asset_id}/ocr | OCRを訂正し新しいrunを保存 | [correct_ocr](api/correct_ocr.detail-design.md) |
| GET | /api/images/ocr/{run_id} | 認可されたOCR領域を取得 | [get_ocr](api/get_ocr.detail-design.md) |
| GET | /api/groups/me | 本人と現在の所属権限を取得 | [get_identity](api/get_identity.detail-design.md) |
| GET | /api/groups/{department_id}/members | 自部署の所属を一覧 | [list_members](api/list_members.detail-design.md) |
| PUT | /api/groups/memberships | 部署の所属権限を変更 | [change_membership](api/change_membership.detail-design.md) |
| POST | /api/metrics/views/{document_id} | 実閲覧を一意IDで記録 | [record_view](api/record_view.detail-design.md) |
| GET | /api/metrics/{department_id} | 部署の利用数と文書貢献を集計 | [department_metrics](api/department_metrics.detail-design.md) |
| GET | /api/operations/jobs | 反映ジョブと失敗理由を確認 | [list_jobs](api/list_jobs.detail-design.md) |
| POST | /api/operations/jobs/{job_id} | 反映ジョブを再処理 | [retry_job](api/retry_job.detail-design.md) |
| GET | /api/operations/reconcile | 正本と索引の不一致を確認 | [reconcile_index](api/reconcile_index.detail-design.md) |
| POST | /api/chat | 最新承認版の根拠で回答 | [ask_question](api/ask_question.detail-design.md) |
| GET | /api/chat/{conversation_id} | 現行認可で会話履歴を再表示 | [chat_history](api/chat_history.detail-design.md) |
