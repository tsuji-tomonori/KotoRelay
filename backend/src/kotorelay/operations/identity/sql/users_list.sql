-- usersを組織境界内でlistする。
SELECT id, organization_id, subject, display_name, active, operator FROM users WHERE organization_id = %(organization_id)s ORDER BY id;
