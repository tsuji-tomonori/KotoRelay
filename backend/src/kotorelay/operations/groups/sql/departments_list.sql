-- departmentsを組織境界内でlistする。
SELECT
    id,
    organization_id,
    name,
    active
FROM departments
WHERE organization_id = %(organization_id)s
ORDER BY id;
