-- 現在の組織の会話を、所有者と開始日時を指定して登録する。
INSERT INTO conversations (id, organization_id, user_id, created_at) VALUES (
    %(id)s, %(organization_id)s, %(user_id)s, %(created_at)s
);
