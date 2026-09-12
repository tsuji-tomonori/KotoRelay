-- organizationsを組織境界内でlistする。
SELECT
    id,
    organization_id,
    name,
    revision,
    suspended
FROM organizations
WHERE organization_id = %(organization_id)s
ORDER BY id;
