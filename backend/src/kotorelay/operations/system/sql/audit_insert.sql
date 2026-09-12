-- 現在の組織の監査記録として、操作した利用者・対象・変更前後の状態・理由を登録する。
INSERT INTO audit (
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
) VALUES (
    %(id)s,
    %(organization_id)s,
    %(user_id)s,
    %(document_id)s,
    %(version_id)s,
    %(action)s,
    %(before_state)s,
    %(after_state)s,
    %(reason)s,
    %(created_at)s
);
