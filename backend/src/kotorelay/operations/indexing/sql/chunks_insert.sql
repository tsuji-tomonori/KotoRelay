-- chunksを組織境界内でinsertする。
INSERT INTO chunks (id, organization_id, document_id, version_id, body_key, sha256, heading, placements, manifest_hash, ready) VALUES (%(id)s, %(organization_id)s, %(document_id)s, %(version_id)s, %(body_key)s, %(sha256)s, %(heading)s, %(placements)s, %(manifest_hash)s, %(ready)s);
