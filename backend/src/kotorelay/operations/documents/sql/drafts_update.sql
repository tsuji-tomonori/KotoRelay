-- 現在の組織に属する指定の下書きについて、本文の保存先・画像配置・改訂番号を更新する。
UPDATE drafts SET
    document_id = %(document_id)s,
    body_key = %(body_key)s,
    body_hash = %(body_hash)s,
    placements = %(placements)s,
    revision = %(revision)s,
    updated_by = %(updated_by)s
WHERE organization_id = %(organization_id)s AND id = %(id)s;
