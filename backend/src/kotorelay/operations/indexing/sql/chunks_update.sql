-- 現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を更新する。
UPDATE chunks SET
    document_id = %(document_id)s,
    version_id = %(version_id)s,
    body_key = %(body_key)s,
    sha256 = %(sha256)s,
    heading = %(heading)s,
    placements = %(placements)s,
    manifest_hash = %(manifest_hash)s,
    ready = %(ready)s
WHERE organization_id = %(organization_id)s AND id = %(id)s;
