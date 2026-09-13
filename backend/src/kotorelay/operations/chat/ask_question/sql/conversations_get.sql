-- 現在の組織に属する指定の会話について、会話の所有者と開始日時を取得する。
SELECT
    id,
    organization_id,
    user_id,
    created_at
FROM conversations
WHERE organization_id = %(organization_id)s AND id = %(id)s;
