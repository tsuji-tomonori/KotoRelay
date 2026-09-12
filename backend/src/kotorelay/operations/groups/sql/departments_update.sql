-- 現在の組織に属する指定の部署について、部署名と有効状態を更新する。
UPDATE departments SET name = %(name)s, active = %(active)s
WHERE organization_id = %(organization_id)s AND id = %(id)s;
