-- 現在の組織に属する指定の回答履歴の記録を削除する。
DELETE FROM answers
WHERE organization_id = %(organization_id)s AND id = %(id)s;
