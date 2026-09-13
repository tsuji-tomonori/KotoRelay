-- 現在の組織に属する反映・削除ジョブを識別子順に一覧取得する。
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
WHERE organization_id = %(organization_id)s
ORDER BY id;
