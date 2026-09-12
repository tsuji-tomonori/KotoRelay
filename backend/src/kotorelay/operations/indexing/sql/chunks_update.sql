-- chunksを組織境界内でupdateする。
UPDATE chunks SET document_id = %(document_id)s, version_id = %(version_id)s, body_key = %(body_key)s, sha256 = %(sha256)s, heading = %(heading)s, placements = %(placements)s, manifest_hash = %(manifest_hash)s, ready = %(ready)s WHERE organization_id = %(organization_id)s AND id = %(id)s;
