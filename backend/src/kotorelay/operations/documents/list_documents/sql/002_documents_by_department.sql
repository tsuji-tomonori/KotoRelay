-- 現在の組織に属する文書を指定した所有部署で絞り込み、一覧の対象を取得する。
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
