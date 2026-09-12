-- outboxを組織境界内でdeleteする。
DELETE FROM outbox
WHERE organization_id = %(organization_id)s AND id = %(id)s;
