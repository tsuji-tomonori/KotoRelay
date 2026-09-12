-- 現在の組織に属する利用者を識別子順に一覧取得する。
SELECT
    id,
    organization_id,
    subject,
    display_name,
    active,
    operator
FROM users
WHERE organization_id = %(organization_id)s
ORDER BY id;
