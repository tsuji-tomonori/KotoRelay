-- 現在の組織に属する会話を識別子順に一覧取得する。
SELECT
    id,
    organization_id,
    user_id,
    created_at
FROM conversations
WHERE organization_id = %(organization_id)s
ORDER BY id;
