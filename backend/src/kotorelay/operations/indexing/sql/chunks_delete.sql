-- 現在の組織に属する指定の検索用の文書断片の記録を削除する。
DELETE FROM chunks
WHERE organization_id = %(organization_id)s AND id = %(id)s;
