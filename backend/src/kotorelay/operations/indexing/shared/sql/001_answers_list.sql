-- 現在の組織に属する回答履歴を識別子順に一覧取得する。
SELECT
    id,
    organization_id,
    conversation_id,
    user_id,
    department_id,
    question_key,
    answer_key,
    evidence,
    status,
    model,
    created_at
FROM answers
WHERE organization_id = %(organization_id)s
ORDER BY id;
