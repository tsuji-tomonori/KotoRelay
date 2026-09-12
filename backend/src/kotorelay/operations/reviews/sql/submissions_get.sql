-- 現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を取得する。
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
WHERE organization_id = %(organization_id)s AND id = %(id)s;
