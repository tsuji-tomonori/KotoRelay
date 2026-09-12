-- answersを組織境界内でupdateする。
UPDATE answers SET conversation_id = %(conversation_id)s, user_id = %(user_id)s, department_id = %(department_id)s, question_key = %(question_key)s, answer_key = %(answer_key)s, evidence = %(evidence)s, status = %(status)s, model = %(model)s, created_at = %(created_at)s WHERE organization_id = %(organization_id)s AND id = %(id)s;
