-- documentsを組織境界内でgetする。
SELECT id, organization_id, department_id, title, created_by, visibility, shared_departments, status, revision, next_version, latest_version_id, updated_at FROM documents WHERE organization_id = %(organization_id)s AND id = %(id)s;
