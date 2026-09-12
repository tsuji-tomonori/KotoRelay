-- organizationsを組織境界内でinsertする。
INSERT INTO organizations (id, organization_id, name, revision, suspended) VALUES (%(id)s, %(organization_id)s, %(name)s, %(revision)s, %(suspended)s);
