-- 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。
UPDATE documents SET
    department_id = %(department_id)s,
    title = %(title)s,
    created_by = %(created_by)s,
    visibility = %(visibility)s,
    shared_departments = %(shared_departments)s,
    status = %(status)s,
    revision = %(revision)s,
    next_version = %(next_version)s,
    latest_version_id = %(latest_version_id)s,
    updated_at = %(updated_at)s
WHERE organization_id = %(organization_id)s AND id = %(id)s;
