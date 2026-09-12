-- membershipsを組織境界内でdeleteする。
DELETE FROM memberships WHERE organization_id = %(organization_id)s AND id = %(id)s;
