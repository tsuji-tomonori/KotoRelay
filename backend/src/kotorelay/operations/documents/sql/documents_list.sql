-- documentsを組織境界内でlistする。
SELECT
    id,
    organization_id,
    department_id,
    title,
    created_by,
    visibility,
    shared_departments,
    status,
    revision,
    next_version,
    latest_version_id,
    updated_at
FROM documents
WHERE organization_id = %(organization_id)s
ORDER BY id;
