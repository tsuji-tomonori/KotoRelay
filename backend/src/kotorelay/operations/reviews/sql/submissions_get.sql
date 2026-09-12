-- submissionsを組織境界内でgetする。
SELECT id, organization_id, document_id, version_id, requested_by, status, manifest_hash, decided_by, reason, created_at, decided_at FROM submissions WHERE organization_id = %(organization_id)s AND id = %(id)s;
