-- 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。
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
WHERE organization_id = %(organization_id)s AND id = %(id)s;
