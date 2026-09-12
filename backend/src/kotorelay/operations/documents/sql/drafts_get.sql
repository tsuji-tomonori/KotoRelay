-- 現在の組織に属する指定の下書きについて、本文の保存先・画像配置・改訂番号を取得する。
SELECT
    id,
    organization_id,
    document_id,
    body_key,
    body_hash,
    placements,
    revision,
    updated_by
FROM drafts
WHERE organization_id = %(organization_id)s AND id = %(id)s;
