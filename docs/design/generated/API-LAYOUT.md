<!-- 実装から生成。直接編集しない。入力SHA256: 987c18a693c5fa5c9f59f732c65771f1c047c0829e22a5d72b689276aae93c56 -->

# APIごとのファイルと責務

参照: lazunex `096e1e580ab1c0670c57e4febad2bd9fdd4698ee` の `src/app/apis/apis/publish_api`。

## health

正本: `backend/src/kotorelay/operations/system/health`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
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
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/documents/create_document/sql/documents_insert.sql`, `backend/src/kotorelay/operations/documents/create_document/sql/drafts_insert.sql`

型付きquery: backend/src/kotorelay/operations/documents/create_document/generated/queries.py

共有処理: 直接参照なし

## list_documents

正本: `backend/src/kotorelay/operations/documents/list_documents`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/documents/list_documents/sql/chunks_list.sql`, `backend/src/kotorelay/operations/documents/list_documents/sql/documents_by_department.sql`, `backend/src/kotorelay/operations/documents/list_documents/sql/documents_list.sql`, `backend/src/kotorelay/operations/documents/list_documents/sql/submissions_list.sql`, `backend/src/kotorelay/operations/documents/list_documents/sql/versions_list.sql`

型付きquery: backend/src/kotorelay/operations/documents/list_documents/generated/queries.py

共有処理: 直接参照なし

## get_draft

正本: `backend/src/kotorelay/operations/documents/get_draft`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: 直接所有なし（共有処理のSQLはAPI別クエリ帳票を参照）

型付きquery: 直接所有なし

共有処理: kotorelay.operations.documents.shared.functions

## save_draft

正本: `backend/src/kotorelay/operations/documents/save_draft`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/documents/save_draft/sql/assets_get.sql`, `backend/src/kotorelay/operations/documents/save_draft/sql/documents_update.sql`, `backend/src/kotorelay/operations/documents/save_draft/sql/drafts_list.sql`, `backend/src/kotorelay/operations/documents/save_draft/sql/drafts_update.sql`, `backend/src/kotorelay/operations/documents/save_draft/sql/ocr_runs_get.sql`

型付きquery: backend/src/kotorelay/operations/documents/save_draft/generated/queries.py

共有処理: kotorelay.operations.documents.shared.functions

## submit_version

正本: `backend/src/kotorelay/operations/documents/submit_version`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/documents/submit_version/sql/assets_get.sql`, `backend/src/kotorelay/operations/documents/submit_version/sql/documents_update.sql`, `backend/src/kotorelay/operations/documents/submit_version/sql/drafts_list.sql`, `backend/src/kotorelay/operations/documents/submit_version/sql/ocr_runs_get.sql`, `backend/src/kotorelay/operations/documents/submit_version/sql/submissions_insert.sql`, `backend/src/kotorelay/operations/documents/submit_version/sql/versions_insert.sql`

型付きquery: backend/src/kotorelay/operations/documents/submit_version/generated/queries.py

共有処理: 直接参照なし

## read_document

正本: `backend/src/kotorelay/operations/documents/read_document`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/documents/read_document/sql/chunks_list.sql`, `backend/src/kotorelay/operations/documents/read_document/sql/documents_get.sql`

型付きquery: backend/src/kotorelay/operations/documents/read_document/generated/queries.py

共有処理: 直接参照なし

## version_history

正本: `backend/src/kotorelay/operations/documents/version_history`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/documents/version_history/sql/submissions_list.sql`, `backend/src/kotorelay/operations/documents/version_history/sql/versions_list.sql`

型付きquery: backend/src/kotorelay/operations/documents/version_history/generated/queries.py

共有処理: 直接参照なし

## version_diff

正本: `backend/src/kotorelay/operations/documents/version_diff`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
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
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/documents/change_policy/sql/departments_list.sql`, `backend/src/kotorelay/operations/documents/change_policy/sql/documents_update.sql`, `backend/src/kotorelay/operations/documents/change_policy/sql/outbox_insert.sql`

型付きquery: backend/src/kotorelay/operations/documents/change_policy/generated/queries.py

共有処理: 直接参照なし

## list_reviews

正本: `backend/src/kotorelay/operations/reviews/list_reviews`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/reviews/list_reviews/sql/departments_list.sql`, `backend/src/kotorelay/operations/reviews/list_reviews/sql/documents_list.sql`, `backend/src/kotorelay/operations/reviews/list_reviews/sql/submissions_list.sql`, `backend/src/kotorelay/operations/reviews/list_reviews/sql/users_list.sql`, `backend/src/kotorelay/operations/reviews/list_reviews/sql/versions_list.sql`

型付きquery: backend/src/kotorelay/operations/reviews/list_reviews/generated/queries.py

共有処理: 直接参照なし

## decide_review

正本: `backend/src/kotorelay/operations/reviews/decide_review`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/reviews/decide_review/sql/documents_update.sql`, `backend/src/kotorelay/operations/reviews/decide_review/sql/outbox_insert.sql`, `backend/src/kotorelay/operations/reviews/decide_review/sql/submissions_get.sql`, `backend/src/kotorelay/operations/reviews/decide_review/sql/submissions_update.sql`, `backend/src/kotorelay/operations/reviews/decide_review/sql/versions_get.sql`

型付きquery: backend/src/kotorelay/operations/reviews/decide_review/generated/queries.py

共有処理: 直接参照なし

## upload_image

正本: `backend/src/kotorelay/operations/images/upload_image`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/images/upload_image/sql/assets_insert.sql`, `backend/src/kotorelay/operations/images/upload_image/sql/assets_list.sql`, `backend/src/kotorelay/operations/images/upload_image/sql/ocr_runs_insert.sql`

型付きquery: backend/src/kotorelay/operations/images/upload_image/generated/queries.py

共有処理: 直接参照なし

## get_image

正本: `backend/src/kotorelay/operations/images/get_image`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: 直接所有なし（共有処理のSQLはAPI別クエリ帳票を参照）

型付きquery: 直接所有なし

共有処理: kotorelay.operations.images.shared.functions

## get_ocr

正本: `backend/src/kotorelay/operations/images/get_ocr`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/images/get_ocr/sql/documents_get.sql`, `backend/src/kotorelay/operations/images/get_ocr/sql/ocr_runs_get.sql`

型付きquery: backend/src/kotorelay/operations/images/get_ocr/generated/queries.py

共有処理: kotorelay.operations.images.shared.functions

## correct_ocr

正本: `backend/src/kotorelay/operations/images/correct_ocr`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/images/correct_ocr/sql/assets_get.sql`, `backend/src/kotorelay/operations/images/correct_ocr/sql/ocr_runs_insert.sql`

型付きquery: backend/src/kotorelay/operations/images/correct_ocr/generated/queries.py

共有処理: 直接参照なし

## get_identity

正本: `backend/src/kotorelay/operations/groups/get_identity`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/groups/get_identity/sql/departments_list.sql`

型付きquery: backend/src/kotorelay/operations/groups/get_identity/generated/queries.py

共有処理: 直接参照なし

## list_members

正本: `backend/src/kotorelay/operations/groups/list_members`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/groups/list_members/sql/memberships_list.sql`, `backend/src/kotorelay/operations/groups/list_members/sql/users_list.sql`

型付きquery: backend/src/kotorelay/operations/groups/list_members/generated/queries.py

共有処理: 直接参照なし

## change_membership

正本: `backend/src/kotorelay/operations/groups/change_membership`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/groups/change_membership/sql/departments_get.sql`, `backend/src/kotorelay/operations/groups/change_membership/sql/memberships_insert.sql`, `backend/src/kotorelay/operations/groups/change_membership/sql/memberships_list.sql`, `backend/src/kotorelay/operations/groups/change_membership/sql/memberships_update.sql`, `backend/src/kotorelay/operations/groups/change_membership/sql/users_get.sql`

型付きquery: backend/src/kotorelay/operations/groups/change_membership/generated/queries.py

共有処理: 直接参照なし

## record_view

正本: `backend/src/kotorelay/operations/metrics/record_view`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/metrics/record_view/sql/events_get.sql`, `backend/src/kotorelay/operations/metrics/record_view/sql/events_insert.sql`

型付きquery: backend/src/kotorelay/operations/metrics/record_view/generated/queries.py

共有処理: 直接参照なし

## department_metrics

正本: `backend/src/kotorelay/operations/metrics/department_metrics`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/metrics/department_metrics/sql/documents_list.sql`, `backend/src/kotorelay/operations/metrics/department_metrics/sql/events_list.sql`

型付きquery: backend/src/kotorelay/operations/metrics/department_metrics/generated/queries.py

共有処理: 直接参照なし

## retry_job

正本: `backend/src/kotorelay/operations/indexing/retry_job`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: 直接所有なし（共有処理のSQLはAPI別クエリ帳票を参照）

型付きquery: 直接所有なし

共有処理: kotorelay.operations.indexing.shared.functions

## list_jobs

正本: `backend/src/kotorelay/operations/indexing/list_jobs`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/indexing/list_jobs/sql/documents_list.sql`, `backend/src/kotorelay/operations/indexing/list_jobs/sql/outbox_list.sql`, `backend/src/kotorelay/operations/indexing/list_jobs/sql/versions_list.sql`

型付きquery: backend/src/kotorelay/operations/indexing/list_jobs/generated/queries.py

共有処理: 直接参照なし

## reconcile_index

正本: `backend/src/kotorelay/operations/indexing/reconcile_index`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/indexing/reconcile_index/sql/chunks_list.sql`, `backend/src/kotorelay/operations/indexing/reconcile_index/sql/documents_list.sql`

型付きquery: backend/src/kotorelay/operations/indexing/reconcile_index/generated/queries.py

共有処理: 直接参照なし

## ask_question

正本: `backend/src/kotorelay/operations/chat/ask_question`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/chat/ask_question/sql/answers_get.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/answers_insert.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/answers_list.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/assets_get.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/chunks_list.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/conversations_get.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/conversations_insert.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/documents_list.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/events_insert.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/events_list.sql`, `backend/src/kotorelay/operations/chat/ask_question/sql/versions_get.sql`

型付きquery: backend/src/kotorelay/operations/chat/ask_question/generated/queries.py

共有処理: kotorelay.operations.chat.shared.functions

## chat_history

正本: `backend/src/kotorelay/operations/chat/chat_history`

| ファイル | 責務 |
| --- | --- |
| router.py | HTTP入力・依存注入・業務処理の順序 |
| functions.py | API固有の業務判定・処理 |
| schemas.py | API固有の入力制約・応答型 |
| response_builders.py | 応答型の検証・HTTP応答への変換 |
| contract.py | operation ID・method/path・認証方式・所有先 |
| samples.py | 実HTTP試験で確認する入力と期待値 |

SQL正本: `backend/src/kotorelay/operations/chat/chat_history/sql/answers_list.sql`, `backend/src/kotorelay/operations/chat/chat_history/sql/conversations_get.sql`

型付きquery: backend/src/kotorelay/operations/chat/chat_history/generated/queries.py

共有処理: kotorelay.operations.chat.shared.functions