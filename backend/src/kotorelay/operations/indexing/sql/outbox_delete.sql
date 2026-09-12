-- 現在の組織に属する指定の反映・削除ジョブの記録を削除する。
DELETE FROM outbox
WHERE organization_id = %(organization_id)s AND id = %(id)s;
