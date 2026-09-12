-- 選択した所有部署の文書をページング前に組織内で絞り込む。
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
WHERE organization_id = %(organization_id)s AND department_id = %(department_id)s;
