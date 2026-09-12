-- 現在の組織の検索用の文書断片を、出典の版・本文の保存先・画像配置とともに登録する。
INSERT INTO chunks (
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
) VALUES (
    %(id)s,
    %(organization_id)s,
    %(document_id)s,
    %(version_id)s,
    %(body_key)s,
    %(sha256)s,
    %(heading)s,
    %(placements)s,
    %(manifest_hash)s,
    %(ready)s
);
