-- usersを組織境界内でinsertする。
INSERT INTO users (id, organization_id, subject, display_name, active, operator) VALUES (%(id)s, %(organization_id)s, %(subject)s, %(display_name)s, %(active)s, %(operator)s);
