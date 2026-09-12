-- 現在の組織に属する下書きを識別子順に一覧取得する。
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
WHERE organization_id = %(organization_id)s
ORDER BY id;
