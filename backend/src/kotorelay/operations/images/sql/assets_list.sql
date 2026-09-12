-- assetsを組織境界内でlistする。
SELECT id, organization_id, document_id, object_key, sha256, media_type, width, height, size, created_at FROM assets WHERE organization_id = %(organization_id)s ORDER BY id;
