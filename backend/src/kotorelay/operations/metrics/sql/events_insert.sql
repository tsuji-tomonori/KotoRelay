-- eventsを組織境界内でinsertする。
INSERT INTO events (
    id, organization_id, user_id, department_id, document_id, answer_id, kind, outcome, created_at
) VALUES (
    %(id)s,
    %(organization_id)s,
    %(user_id)s,
    %(department_id)s,
    %(document_id)s,
    %(answer_id)s,
    %(kind)s,
    %(outcome)s,
    %(created_at)s
);
