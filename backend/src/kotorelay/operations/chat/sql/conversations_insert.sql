-- conversationsを組織境界内でinsertする。
INSERT INTO conversations (id, organization_id, user_id, created_at) VALUES (
    %(id)s, %(organization_id)s, %(user_id)s, %(created_at)s
);
