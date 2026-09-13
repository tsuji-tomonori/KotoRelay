-- 現在の組織に属する部署所属を識別子順に一覧取得する。
SELECT
    id,
    organization_id,
    department_id,
    user_id,
    leader,
    can_author,
    can_review,
    active
FROM memberships
WHERE organization_id = %(organization_id)s
ORDER BY id;
