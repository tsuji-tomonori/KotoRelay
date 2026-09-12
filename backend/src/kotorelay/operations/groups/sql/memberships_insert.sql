-- membershipsを組織境界内でinsertする。
INSERT INTO memberships (id, organization_id, department_id, user_id, leader, can_author, can_review, active) VALUES (%(id)s, %(organization_id)s, %(department_id)s, %(user_id)s, %(leader)s, %(can_author)s, %(can_review)s, %(active)s);
