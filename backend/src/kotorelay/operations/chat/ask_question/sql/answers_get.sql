-- 現在の組織に属する指定の回答履歴について、質問・回答の保存先と根拠・回答状態を取得する。
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
