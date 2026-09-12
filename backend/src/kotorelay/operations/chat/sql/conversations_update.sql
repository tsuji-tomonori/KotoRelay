-- conversationsを組織境界内でupdateする。
UPDATE conversations SET user_id = %(user_id)s, created_at = %(created_at)s
WHERE organization_id = %(organization_id)s AND id = %(id)s;
