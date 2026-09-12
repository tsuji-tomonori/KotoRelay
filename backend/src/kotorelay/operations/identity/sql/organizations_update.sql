-- 現在の組織の組織名・改訂番号・利用停止状態を更新する。
UPDATE organizations SET name = %(name)s, revision = %(revision)s, suspended = %(suspended)s
WHERE organization_id = %(organization_id)s AND id = %(id)s;
