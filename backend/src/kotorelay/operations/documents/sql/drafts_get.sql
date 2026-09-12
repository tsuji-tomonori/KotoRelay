-- draftsを組織境界内でgetする。
SELECT id, organization_id, document_id, body_key, body_hash, placements, revision, updated_by FROM drafts WHERE organization_id = %(organization_id)s AND id = %(id)s;
