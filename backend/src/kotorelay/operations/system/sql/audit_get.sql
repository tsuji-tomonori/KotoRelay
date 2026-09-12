-- 現在の組織に属する指定の監査記録について、操作した利用者・対象・変更前後の状態・理由を取得する。
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
