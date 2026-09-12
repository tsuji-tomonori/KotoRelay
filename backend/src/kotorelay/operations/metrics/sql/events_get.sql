-- eventsを組織境界内でgetする。
SELECT id, organization_id, user_id, department_id, document_id, answer_id, kind, outcome, created_at FROM events WHERE organization_id = %(organization_id)s AND id = %(id)s;
