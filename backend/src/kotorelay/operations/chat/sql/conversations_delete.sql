-- 現在の組織に属する指定の会話の記録を削除する。
DELETE FROM conversations
WHERE organization_id = %(organization_id)s AND id = %(id)s;
