-- draftsを組織境界内でdeleteする。
DELETE FROM drafts
WHERE organization_id = %(organization_id)s AND id = %(id)s;
