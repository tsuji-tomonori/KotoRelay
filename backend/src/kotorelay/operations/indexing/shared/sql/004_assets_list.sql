-- 現在の組織に属する添付画像を識別子順に一覧取得する。
SELECT
    id,
    organization_id,
    document_id,
    object_key,
    sha256,
    media_type,
    width,
    height,
    size,
    created_at
FROM assets
WHERE organization_id = %(organization_id)s
ORDER BY id;
