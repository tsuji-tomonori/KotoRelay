-- idempotencyを組織境界内でinsertする。
INSERT INTO idempotency (id, organization_id, user_id, operation, request_hash, response) VALUES (
    %(id)s, %(organization_id)s, %(user_id)s, %(operation)s, %(request_hash)s, %(response)s
);
