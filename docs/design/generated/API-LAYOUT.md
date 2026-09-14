<!-- 実装から生成。直接編集しない。入力SHA256: ac3b8a89c10fb6f4c0a9456ea4fb59251414105722d4188a0beaca0d8b493f26 -->

# APIごとのファイルと責務

参照: lazunex `096e1e580ab1c0670c57e4febad2bd9fdd4698ee` の `src/app/apis/apis/publish_api`。

## health

正本: `backend/src/kotorelay/operations/system/health`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: 直接所有なし（共有処理のSQLはAPI別クエリ帳票を参照）

型付きquery: 直接所有なし

共有処理: 直接参照なし

## create_document

正本: `backend/src/kotorelay/operations/documents/create_document`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/documents/create_document/sql/001_documents_insert.sql`, `backend/src/kotorelay/operations/documents/create_document/sql/002_drafts_insert.sql`

型付きquery: backend/src/kotorelay/operations/documents/create_document/generated/queries.py

共有処理: 直接参照なし

## list_documents

正本: `backend/src/kotorelay/operations/documents/list_documents`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/documents/list_documents/sql/001_chunks_list.sql`, `backend/src/kotorelay/operations/documents/list_documents/sql/002_documents_by_department.sql`, `backend/src/kotorelay/operations/documents/list_documents/sql/003_documents_list.sql`, `backend/src/kotorelay/operations/documents/list_documents/sql/004_submissions_list.sql`, `backend/src/kotorelay/operations/documents/list_documents/sql/005_versions_list.sql`

型付きquery: backend/src/kotorelay/operations/documents/list_documents/generated/queries.py

共有処理: 直接参照なし

## get_draft

正本: `backend/src/kotorelay/operations/documents/get_draft`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: 直接所有なし（共有処理のSQLはAPI別クエリ帳票を参照）

型付きquery: 直接所有なし

共有処理: 直接参照なし

## save_draft

正本: `backend/src/kotorelay/operations/documents/save_draft`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/documents/save_draft/sql/001_assets_get.sql`, `backend/src/kotorelay/operations/documents/save_draft/sql/002_documents_update.sql`, `backend/src/kotorelay/operations/documents/save_draft/sql/003_drafts_list.sql`, `backend/src/kotorelay/operations/documents/save_draft/sql/004_drafts_update.sql`, `backend/src/kotorelay/operations/documents/save_draft/sql/005_ocr_runs_get.sql`

型付きquery: backend/src/kotorelay/operations/documents/save_draft/generated/queries.py

共有処理: 直接参照なし

## submit_version

正本: `backend/src/kotorelay/operations/documents/submit_version`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/documents/submit_version/sql/001_assets_get.sql`, `backend/src/kotorelay/operations/documents/submit_version/sql/002_documents_update.sql`, `backend/src/kotorelay/operations/documents/submit_version/sql/003_drafts_list.sql`, `backend/src/kotorelay/operations/documents/submit_version/sql/004_ocr_runs_get.sql`, `backend/src/kotorelay/operations/documents/submit_version/sql/005_submissions_insert.sql`, `backend/src/kotorelay/operations/documents/submit_version/sql/006_versions_insert.sql`

型付きquery: backend/src/kotorelay/operations/documents/submit_version/generated/queries.py

共有処理: 直接参照なし

## read_document

正本: `backend/src/kotorelay/operations/documents/read_document`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/documents/read_document/sql/001_chunks_list.sql`, `backend/src/kotorelay/operations/documents/read_document/sql/002_documents_get.sql`

型付きquery: backend/src/kotorelay/operations/documents/read_document/generated/queries.py

共有処理: 直接参照なし

## version_history

正本: `backend/src/kotorelay/operations/documents/version_history`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/documents/version_history/sql/001_submissions_list.sql`, `backend/src/kotorelay/operations/documents/version_history/sql/002_versions_list.sql`

型付きquery: backend/src/kotorelay/operations/documents/version_history/generated/queries.py

共有処理: 直接参照なし

## version_diff

正本: `backend/src/kotorelay/operations/documents/version_diff`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: 直接所有なし（共有処理のSQLはAPI別クエリ帳票を参照）

型付きquery: 直接所有なし

共有処理: 直接参照なし

## change_policy

正本: `backend/src/kotorelay/operations/documents/change_policy`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/documents/change_policy/sql/001_departments_list.sql`, `backend/src/kotorelay/operations/documents/change_policy/sql/002_documents_update.sql`, `backend/src/kotorelay/operations/documents/change_policy/sql/003_outbox_insert.sql`

型付きquery: backend/src/kotorelay/operations/documents/change_policy/generated/queries.py

共有処理: 直接参照なし

## list_reviews

正本: `backend/src/kotorelay/operations/reviews/list_reviews`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/reviews/list_reviews/sql/001_departments_list.sql`, `backend/src/kotorelay/operations/reviews/list_reviews/sql/002_documents_list.sql`, `backend/src/kotorelay/operations/reviews/list_reviews/sql/003_submissions_list.sql`, `backend/src/kotorelay/operations/reviews/list_reviews/sql/004_users_list.sql`, `backend/src/kotorelay/operations/reviews/list_reviews/sql/005_versions_list.sql`

型付きquery: backend/src/kotorelay/operations/reviews/list_reviews/generated/queries.py

共有処理: 直接参照なし

## decide_review

正本: `backend/src/kotorelay/operations/reviews/decide_review`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/reviews/decide_review/sql/001_documents_update.sql`, `backend/src/kotorelay/operations/reviews/decide_review/sql/002_outbox_insert.sql`, `backend/src/kotorelay/operations/reviews/decide_review/sql/003_submissions_get.sql`, `backend/src/kotorelay/operations/reviews/decide_review/sql/004_submissions_update.sql`, `backend/src/kotorelay/operations/reviews/decide_review/sql/005_versions_get.sql`

型付きquery: backend/src/kotorelay/operations/reviews/decide_review/generated/queries.py

共有処理: 直接参照なし

## upload_image

正本: `backend/src/kotorelay/operations/images/upload_image`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/images/upload_image/sql/001_assets_insert.sql`, `backend/src/kotorelay/operations/images/upload_image/sql/002_assets_list.sql`, `backend/src/kotorelay/operations/images/upload_image/sql/003_ocr_runs_insert.sql`

型付きquery: backend/src/kotorelay/operations/images/upload_image/generated/queries.py

共有処理: 直接参照なし

## get_image

正本: `backend/src/kotorelay/operations/images/get_image`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: 直接所有なし（共有処理のSQLはAPI別クエリ帳票を参照）

型付きquery: 直接所有なし

共有処理: 直接参照なし

## get_ocr

正本: `backend/src/kotorelay/operations/images/get_ocr`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/images/get_ocr/sql/001_documents_get.sql`, `backend/src/kotorelay/operations/images/get_ocr/sql/002_ocr_runs_get.sql`

型付きquery: backend/src/kotorelay/operations/images/get_ocr/generated/queries.py

共有処理: 直接参照なし

## correct_ocr

正本: `backend/src/kotorelay/operations/images/correct_ocr`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/images/correct_ocr/sql/001_assets_get.sql`, `backend/src/kotorelay/operations/images/correct_ocr/sql/002_ocr_runs_insert.sql`

型付きquery: backend/src/kotorelay/operations/images/correct_ocr/generated/queries.py

共有処理: 直接参照なし

## get_identity

正本: `backend/src/kotorelay/operations/groups/get_identity`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/groups/get_identity/sql/001_departments_list.sql`

型付きquery: backend/src/kotorelay/operations/groups/get_identity/generated/queries.py

共有処理: 直接参照なし

## list_members

正本: `backend/src/kotorelay/operations/groups/list_members`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/groups/list_members/sql/001_memberships_list.sql`, `backend/src/kotorelay/operations/groups/list_members/sql/002_users_list.sql`

型付きquery: backend/src/kotorelay/operations/groups/list_members/generated/queries.py

共有処理: 直接参照なし

## change_membership

正本: `backend/src/kotorelay/operations/groups/change_membership`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/groups/change_membership/sql/001_departments_get.sql`, `backend/src/kotorelay/operations/groups/change_membership/sql/002_memberships_insert.sql`, `backend/src/kotorelay/operations/groups/change_membership/sql/003_memberships_list.sql`, `backend/src/kotorelay/operations/groups/change_membership/sql/004_memberships_update.sql`, `backend/src/kotorelay/operations/groups/change_membership/sql/005_users_get.sql`

型付きquery: backend/src/kotorelay/operations/groups/change_membership/generated/queries.py

共有処理: 直接参照なし

## record_view

正本: `backend/src/kotorelay/operations/metrics/record_view`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/metrics/record_view/sql/001_events_get.sql`, `backend/src/kotorelay/operations/metrics/record_view/sql/002_events_insert.sql`

型付きquery: backend/src/kotorelay/operations/metrics/record_view/generated/queries.py

共有処理: 直接参照なし

## department_metrics

正本: `backend/src/kotorelay/operations/metrics/department_metrics`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/metrics/department_metrics/sql/001_documents_list.sql`, `backend/src/kotorelay/operations/metrics/department_metrics/sql/002_events_list.sql`

型付きquery: backend/src/kotorelay/operations/metrics/department_metrics/generated/queries.py

共有処理: 直接参照なし

## retry_job

正本: `backend/src/kotorelay/operations/indexing/retry_job`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: 直接所有なし（共有処理のSQLはAPI別クエリ帳票を参照）

型付きquery: 直接所有なし

共有処理: 直接参照なし

## list_jobs

正本: `backend/src/kotorelay/operations/indexing/list_jobs`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/indexing/list_jobs/sql/001_documents_list.sql`, `backend/src/kotorelay/operations/indexing/list_jobs/sql/002_outbox_list.sql`, `backend/src/kotorelay/operations/indexing/list_jobs/sql/003_versions_list.sql`

型付きquery: backend/src/kotorelay/operations/indexing/list_jobs/generated/queries.py

共有処理: 直接参照なし

## reconcile_index

正本: `backend/src/kotorelay/operations/indexing/reconcile_index`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/indexing/reconcile_index/sql/001_chunks_list.sql`, `backend/src/kotorelay/operations/indexing/reconcile_index/sql/002_documents_list.sql`

型付きquery: backend/src/kotorelay/operations/indexing/reconcile_index/generated/queries.py

共有処理: 直接参照なし

## ask_question

正本: `backend/src/kotorelay/operations/chat/ask_question`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/chat/ask_question/sql/001_answers_get.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/002_answers_insert.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/003_answers_list.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/004_assets_get.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/005_chunks_list.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/006_conversations_get.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/007_conversations_insert.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/008_documents_list.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/009_events_insert.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/010_events_list.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/011_versions_get.sql`

型付きquery: backend/src/kotorelay/operations/chat/ask_question/generated/queries.py

共有処理: 直接参照なし

## chat_history

正本: `backend/src/kotorelay/operations/chat/chat_history`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・全体フロー・分岐・例外・transaction |
| functions.py | 全体フローを持たない個別の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/chat/chat_history/sql/001_answers_list.sql`, `backend/src/kotorelay/operations/chat/chat_history/sql/002_conversations_get.sql`

型付きquery: backend/src/kotorelay/operations/chat/chat_history/generated/queries.py

共有処理: kotorelay.operations.chat.shared.functions