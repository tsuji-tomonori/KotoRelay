-- 現在の組織に属する再送判定の記録を識別子順に一覧取得する。
SELECT
    id,
    organization_id,
    user_id,
    operation,
    request_hash,
    response
FROM idempotency
WHERE organization_id = %(organization_id)s
ORDER BY id;
