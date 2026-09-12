-- idempotencyを組織境界内でgetする。
SELECT
    id,
    organization_id,
    user_id,
    operation,
    request_hash,
    response
FROM idempotency
WHERE organization_id = %(organization_id)s AND id = %(id)s;
