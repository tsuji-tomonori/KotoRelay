-- 現在の組織に属する指定の承認申請の記録を削除する。
DELETE FROM submissions
WHERE organization_id = %(organization_id)s AND id = %(id)s;
