-- 現在の組織に属する指定の利用者について、認証主体・表示名・有効状態・運用権限を取得する。
SELECT
    id,
    organization_id,
    subject,
    display_name,
    active,
    operator
FROM users
WHERE organization_id = %(organization_id)s AND id = %(id)s;
