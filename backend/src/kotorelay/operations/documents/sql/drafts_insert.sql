-- draftsを組織境界内でinsertする。
INSERT INTO drafts (id, organization_id, document_id, body_key, body_hash, placements, revision, updated_by) VALUES (%(id)s, %(organization_id)s, %(document_id)s, %(body_key)s, %(body_hash)s, %(placements)s, %(revision)s, %(updated_by)s);
