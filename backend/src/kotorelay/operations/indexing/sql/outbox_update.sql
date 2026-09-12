-- outboxを組織境界内でupdateする。
UPDATE outbox SET
    document_id = %(document_id)s,
    version_id = %(version_id)s,
    kind = %(kind)s,
    status = %(status)s,
    attempts = %(attempts)s,
    error_code = %(error_code)s,
    created_at = %(created_at)s
WHERE organization_id = %(organization_id)s AND id = %(id)s;
