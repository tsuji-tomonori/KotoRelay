-- conversationsを組織境界内でlistする。
SELECT
    id,
    organization_id,
    user_id,
    created_at
FROM conversations
WHERE organization_id = %(organization_id)s
ORDER BY id;
