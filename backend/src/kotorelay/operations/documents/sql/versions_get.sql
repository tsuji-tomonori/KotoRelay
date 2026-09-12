-- versionsを組織境界内でgetする。
SELECT id, organization_id, document_id, number, title, body_key, body_hash, manifest, manifest_hash, created_by, created_at FROM versions WHERE organization_id = %(organization_id)s AND id = %(id)s;
