-- outboxを組織境界内でlistする。
SELECT
    id,
    organization_id,
    document_id,
    version_id,
    kind,
    status,
    attempts,
    error_code,
    created_at
FROM outbox
WHERE organization_id = %(organization_id)s
ORDER BY id;
