-- idempotencyを組織境界内でlistする。
SELECT id, organization_id, user_id, operation, request_hash, response FROM idempotency WHERE organization_id = %(organization_id)s ORDER BY id;
