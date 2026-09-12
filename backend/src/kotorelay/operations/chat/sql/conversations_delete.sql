-- conversationsを組織境界内でdeleteする。
DELETE FROM conversations WHERE organization_id = %(organization_id)s AND id = %(id)s;
