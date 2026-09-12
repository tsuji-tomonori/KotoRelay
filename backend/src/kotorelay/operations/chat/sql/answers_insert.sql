-- 現在の組織の回答履歴として、質問者・利用部署・質問と回答の保存先・根拠を登録する。
INSERT INTO answers (
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
) VALUES (
    %(id)s,
    %(organization_id)s,
    %(conversation_id)s,
    %(user_id)s,
    %(department_id)s,
    %(question_key)s,
    %(answer_key)s,
    %(evidence)s,
    %(status)s,
    %(model)s,
    %(created_at)s
);
