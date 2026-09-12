-- organizationsを組織境界内でgetする。
SELECT
    id,
    organization_id,
    name,
    revision,
    suspended
FROM organizations
WHERE organization_id = %(organization_id)s AND id = %(id)s;
