-- 現在の組織に属する指定の文書版の記録を削除する。
DELETE FROM versions
WHERE organization_id = %(organization_id)s AND id = %(id)s;
