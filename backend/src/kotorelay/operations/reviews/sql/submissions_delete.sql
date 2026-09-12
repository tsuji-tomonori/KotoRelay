-- submissionsを組織境界内でdeleteする。
DELETE FROM submissions
WHERE organization_id = %(organization_id)s AND id = %(id)s;
