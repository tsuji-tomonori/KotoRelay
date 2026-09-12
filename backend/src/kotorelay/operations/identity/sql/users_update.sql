-- 現在の組織に属する指定の利用者について、認証主体・表示名・有効状態・運用権限を更新する。
UPDATE users SET
    subject = %(subject)s,
    display_name = %(display_name)s,
    active = %(active)s,
    operator = %(operator)s
WHERE organization_id = %(organization_id)s AND id = %(id)s;
