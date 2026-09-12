-- 現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を取得する。
SELECT
    id,
    organization_id,
    document_id,
    version_id,
    kind,
    status,
    attempts,
    error_code,
    created_at
FROM outbox
WHERE organization_id = %(organization_id)s AND id = %(id)s;
