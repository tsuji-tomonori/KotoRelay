-- answersを組織境界内でgetする。
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
WHERE organization_id = %(organization_id)s AND id = %(id)s;
