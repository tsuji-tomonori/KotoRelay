-- 組織を、組織名・改訂番号・利用停止状態を指定して登録する。
INSERT INTO organizations (id, organization_id, name, revision, suspended) VALUES (
    %(id)s, %(organization_id)s, %(name)s, %(revision)s, %(suspended)s
);
