-- 現在の組織に属する指定の利用イベントについて、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を取得する。
SELECT
    id,
    organization_id,
    user_id,
    department_id,
    document_id,
    answer_id,
    kind,
    outcome,
    created_at
FROM events
WHERE organization_id = %(organization_id)s AND id = %(id)s;
