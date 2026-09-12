-- versionsを組織境界内でdeleteする。
DELETE FROM versions WHERE organization_id = %(organization_id)s AND id = %(id)s;
