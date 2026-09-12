-- 現在の組織に属する指定の部署所属について、所属部署・利用者・執筆や審査の権限・有効状態を更新する。
UPDATE memberships SET
    department_id = %(department_id)s,
    user_id = %(user_id)s,
    leader = %(leader)s,
    can_author = %(can_author)s,
    can_review = %(can_review)s,
    active = %(active)s
WHERE organization_id = %(organization_id)s AND id = %(id)s;
