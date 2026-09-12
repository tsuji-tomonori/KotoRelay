-- assetsを組織境界内でdeleteする。
DELETE FROM assets
WHERE organization_id = %(organization_id)s AND id = %(id)s;
