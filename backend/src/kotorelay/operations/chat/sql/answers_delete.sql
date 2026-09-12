-- answersを組織境界内でdeleteする。
DELETE FROM answers
WHERE organization_id = %(organization_id)s AND id = %(id)s;
