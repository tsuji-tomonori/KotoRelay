-- membershipsを組織境界内でgetする。
SELECT id, organization_id, department_id, user_id, leader, can_author, can_review, active FROM memberships WHERE organization_id = %(organization_id)s AND id = %(id)s;
