-- auditを組織境界内でgetする。
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
WHERE organization_id = %(organization_id)s AND id = %(id)s;
