-- 現在の組織に属する指定の部署について、部署名と有効状態を取得する。
SELECT
    id,
    organization_id,
    name,
    active
FROM departments
WHERE organization_id = %(organization_id)s AND id = %(id)s;
