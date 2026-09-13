-- 現在の組織に属する承認申請を識別子順に一覧取得する。
SELECT
    id,
    organization_id,
    document_id,
    version_id,
    requested_by,
    status,
    manifest_hash,
    decided_by,
    reason,
    created_at,
    decided_at
FROM submissions
WHERE organization_id = %(organization_id)s
ORDER BY id;
