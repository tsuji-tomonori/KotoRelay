-- draftsを組織境界内でupdateする。
UPDATE drafts SET
    document_id = %(document_id)s,
    body_key = %(body_key)s,
    body_hash = %(body_hash)s,
    placements = %(placements)s,
    revision = %(revision)s,
    updated_by = %(updated_by)s
WHERE organization_id = %(organization_id)s AND id = %(id)s;
