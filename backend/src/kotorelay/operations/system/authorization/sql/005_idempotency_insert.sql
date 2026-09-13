-- 現在の組織の操作の再送を判定するため、実行済み操作の入力ハッシュと応答を登録する。
INSERT INTO idempotency (id, organization_id, user_id, operation, request_hash, response) VALUES (
    %(id)s, %(organization_id)s, %(user_id)s, %(operation)s, %(request_hash)s, %(response)s
);
