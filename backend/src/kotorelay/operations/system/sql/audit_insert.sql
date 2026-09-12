-- auditを組織境界内でinsertする。
INSERT INTO audit (id, organization_id, user_id, document_id, version_id, action, before_state, after_state, reason, created_at) VALUES (%(id)s, %(organization_id)s, %(user_id)s, %(document_id)s, %(version_id)s, %(action)s, %(before_state)s, %(after_state)s, %(reason)s, %(created_at)s);
