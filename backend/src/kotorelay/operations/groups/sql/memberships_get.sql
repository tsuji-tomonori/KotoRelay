-- 現在の組織に属する指定の部署所属について、所属部署・利用者・執筆や審査の権限・有効状態を取得する。
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
WHERE organization_id = %(organization_id)s AND id = %(id)s;
