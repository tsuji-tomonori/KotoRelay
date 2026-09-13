-- 現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を取得する。
SELECT
    id,
    organization_id,
    document_id,
    version_id,
    body_key,
    sha256,
    heading,
    placements,
    manifest_hash,
    ready
FROM chunks
WHERE organization_id = %(organization_id)s AND id = %(id)s;
