-- 現在の組織に属する検索用の文書断片を識別子順に一覧取得する。
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
WHERE organization_id = %(organization_id)s
ORDER BY id;
