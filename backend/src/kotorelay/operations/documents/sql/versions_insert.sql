-- 現在の組織の文書版を、版番号・本文の保存先・画像構成・検証用ハッシュを指定して登録する。
INSERT INTO versions (
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
) VALUES (
    %(id)s,
    %(organization_id)s,
    %(document_id)s,
    %(number)s,
    %(title)s,
    %(body_key)s,
    %(body_hash)s,
    %(manifest)s,
    %(manifest_hash)s,
    %(created_by)s,
    %(created_at)s
);
