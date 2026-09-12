-- 現在の組織に属する文書版を識別子順に一覧取得する。
SELECT
    id,
    organization_id,
    document_id,
    number,
    title,
    body_key,
    body_hash,
    manifest,
    manifest_hash,
    created_by,
    created_at
FROM versions
WHERE organization_id = %(organization_id)s
ORDER BY id;
