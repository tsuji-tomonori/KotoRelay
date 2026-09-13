-- 現在の組織の文書に添付した画像の保存先・形式・寸法・検証用ハッシュを登録する。
INSERT INTO assets (
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
) VALUES (
    %(id)s,
    %(organization_id)s,
    %(document_id)s,
    %(object_key)s,
    %(sha256)s,
    %(media_type)s,
    %(width)s,
    %(height)s,
    %(size)s,
    %(created_at)s
);
