-- 現在の組織に属する指定の添付画像の記録を削除する。
DELETE FROM assets
WHERE organization_id = %(organization_id)s AND id = %(id)s;
