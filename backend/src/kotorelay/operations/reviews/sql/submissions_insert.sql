-- submissionsを組織境界内でinsertする。
INSERT INTO submissions (id, organization_id, document_id, version_id, requested_by, status, manifest_hash, decided_by, reason, created_at, decided_at) VALUES (%(id)s, %(organization_id)s, %(document_id)s, %(version_id)s, %(requested_by)s, %(status)s, %(manifest_hash)s, %(decided_by)s, %(reason)s, %(created_at)s, %(decided_at)s);
