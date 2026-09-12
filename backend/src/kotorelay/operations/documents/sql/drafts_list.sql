-- draftsを組織境界内でlistする。
SELECT id, organization_id, document_id, body_key, body_hash, placements, revision, updated_by FROM drafts WHERE organization_id = %(organization_id)s ORDER BY id;
