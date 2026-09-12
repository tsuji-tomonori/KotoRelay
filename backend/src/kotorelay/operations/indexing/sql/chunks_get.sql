-- chunksを組織境界内でgetする。
SELECT
    id,
    organization_id,
    document_id,
    version_id,
    body_key,
    sha256,
    heading,
    placements,
    manifest_hash,
    ready
FROM chunks
WHERE organization_id = %(organization_id)s AND id = %(id)s;
