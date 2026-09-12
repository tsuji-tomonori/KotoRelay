-- departmentsを組織境界内でupdateする。
UPDATE departments SET name = %(name)s, active = %(active)s
WHERE organization_id = %(organization_id)s AND id = %(id)s;
