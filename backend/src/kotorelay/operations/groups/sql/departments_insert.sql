-- departmentsを組織境界内でinsertする。
INSERT INTO departments (id, organization_id, name, active) VALUES (
    %(id)s, %(organization_id)s, %(name)s, %(active)s
);
