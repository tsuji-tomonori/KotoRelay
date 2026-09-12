-- 現在の組織の組織名・改訂番号・利用停止状態を取得する。
SELECT
    id,
    organization_id,
    name,
    revision,
    suspended
FROM organizations
WHERE organization_id = %(organization_id)s AND id = %(id)s;
