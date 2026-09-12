-- departmentsを組織境界内でgetする。
SELECT
    id,
    organization_id,
    name,
    active
FROM departments
WHERE organization_id = %(organization_id)s AND id = %(id)s;
