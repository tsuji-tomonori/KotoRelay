-- 現在の組織に属する指定の回答履歴について、質問・回答の保存先と根拠・回答状態を更新する。
UPDATE answers SET
    conversation_id = %(conversation_id)s,
    user_id = %(user_id)s,
    department_id = %(department_id)s,
    question_key = %(question_key)s,
    answer_key = %(answer_key)s,
    evidence = %(evidence)s,
    status = %(status)s,
    model = %(model)s,
    created_at = %(created_at)s
WHERE organization_id = %(organization_id)s AND id = %(id)s;
