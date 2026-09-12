-- assetsを組織境界内でinsertする。
INSERT INTO assets (id, organization_id, document_id, object_key, sha256, media_type, width, height, size, created_at) VALUES (%(id)s, %(organization_id)s, %(document_id)s, %(object_key)s, %(sha256)s, %(media_type)s, %(width)s, %(height)s, %(size)s, %(created_at)s);
