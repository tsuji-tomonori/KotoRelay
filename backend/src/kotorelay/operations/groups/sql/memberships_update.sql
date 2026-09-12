-- membershipsを組織境界内でupdateする。
UPDATE memberships SET
    department_id = %(department_id)s,
    user_id = %(user_id)s,
    leader = %(leader)s,
    can_author = %(can_author)s,
    can_review = %(can_review)s,
    active = %(active)s
WHERE organization_id = %(organization_id)s AND id = %(id)s;
