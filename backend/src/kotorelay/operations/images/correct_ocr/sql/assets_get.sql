-- 現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。
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
WHERE organization_id = %(organization_id)s AND id = %(id)s;
