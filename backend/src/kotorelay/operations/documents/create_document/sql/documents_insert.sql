-- 現在の組織の文書を、所有部署・公開範囲・状態を指定して登録する。
INSERT INTO documents (
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
) VALUES (
    %(id)s,
    %(organization_id)s,
    %(department_id)s,
    %(title)s,
    %(created_by)s,
    %(visibility)s,
    %(shared_departments)s,
    %(status)s,
    %(revision)s,
    %(next_version)s,
    %(latest_version_id)s,
    %(updated_at)s
);
