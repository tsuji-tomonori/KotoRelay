-- 現在の組織に属する文書を識別子順に一覧取得する。
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
