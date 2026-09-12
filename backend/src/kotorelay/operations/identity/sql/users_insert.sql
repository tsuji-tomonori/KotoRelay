-- 現在の組織の利用者を、認証主体・表示名・有効状態・運用権限を指定して登録する。
INSERT INTO users (id, organization_id, subject, display_name, active, operator) VALUES (
    %(id)s, %(organization_id)s, %(subject)s, %(display_name)s, %(active)s, %(operator)s
);
