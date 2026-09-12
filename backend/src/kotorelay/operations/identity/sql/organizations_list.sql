-- 現在の組織に一致する組織レコードを識別子順に一覧取得する。
SELECT
    id,
    organization_id,
    name,
    revision,
    suspended
FROM organizations
WHERE organization_id = %(organization_id)s
ORDER BY id;
