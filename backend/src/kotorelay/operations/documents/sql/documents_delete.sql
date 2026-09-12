-- documentsを組織境界内でdeleteする。
DELETE FROM documents
WHERE organization_id = %(organization_id)s AND id = %(id)s;
