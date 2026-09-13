-- 現在の組織の部署を、部署名と有効状態を指定して登録する。
INSERT INTO departments (id, organization_id, name, active) VALUES (
    %(id)s, %(organization_id)s, %(name)s, %(active)s
);
