-- chunksを組織境界内でdeleteする。
DELETE FROM chunks WHERE organization_id = %(organization_id)s AND id = %(id)s;
