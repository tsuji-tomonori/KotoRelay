-- 現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を更新する。
UPDATE submissions SET
    document_id = %(document_id)s,
    version_id = %(version_id)s,
    requested_by = %(requested_by)s,
    status = %(status)s,
    manifest_hash = %(manifest_hash)s,
    decided_by = %(decided_by)s,
    reason = %(reason)s,
    created_at = %(created_at)s,
    decided_at = %(decided_at)s
WHERE organization_id = %(organization_id)s AND id = %(id)s;
