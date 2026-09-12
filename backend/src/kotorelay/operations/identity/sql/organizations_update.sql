-- organizationsを組織境界内でupdateする。
UPDATE organizations SET name = %(name)s, revision = %(revision)s, suspended = %(suspended)s
WHERE organization_id = %(organization_id)s AND id = %(id)s;
