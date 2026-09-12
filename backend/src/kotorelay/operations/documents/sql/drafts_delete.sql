-- 現在の組織に属する指定の下書きの記録を削除する。
DELETE FROM drafts
WHERE organization_id = %(organization_id)s AND id = %(id)s;
