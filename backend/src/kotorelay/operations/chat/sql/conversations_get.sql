-- conversationsを組織境界内でgetする。
SELECT id, organization_id, user_id, created_at FROM conversations WHERE organization_id = %(organization_id)s AND id = %(id)s;
