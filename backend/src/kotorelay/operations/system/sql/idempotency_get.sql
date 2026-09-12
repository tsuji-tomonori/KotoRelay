-- 現在の組織に属する指定の再送判定の記録について、実行済み操作の入力ハッシュと応答を取得する。
SELECT
    id,
    organization_id,
    user_id,
    operation,
    request_hash,
    response
FROM idempotency
WHERE organization_id = %(organization_id)s AND id = %(id)s;
