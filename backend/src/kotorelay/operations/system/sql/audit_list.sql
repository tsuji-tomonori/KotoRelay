-- 現在の組織に属する監査記録を識別子順に一覧取得する。
SELECT
    id,
    organization_id,
    user_id,
    document_id,
    version_id,
    action,
    before_state,
    after_state,
    reason,
    created_at
FROM audit
WHERE organization_id = %(organization_id)s
ORDER BY id;
