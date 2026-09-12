-- 現在の組織に属する指定の会話について、会話の所有者と開始日時を更新する。
UPDATE conversations SET user_id = %(user_id)s, created_at = %(created_at)s
WHERE organization_id = %(organization_id)s AND id = %(id)s;
