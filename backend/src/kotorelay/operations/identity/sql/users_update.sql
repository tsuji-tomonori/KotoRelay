-- usersを組織境界内でupdateする。
UPDATE users SET
    subject = %(subject)s,
    display_name = %(display_name)s,
    active = %(active)s,
    operator = %(operator)s
WHERE organization_id = %(organization_id)s AND id = %(id)s;
