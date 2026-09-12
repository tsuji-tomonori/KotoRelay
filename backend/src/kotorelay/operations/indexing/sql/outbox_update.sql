-- 現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。
UPDATE outbox SET
    document_id = %(document_id)s,
    version_id = %(version_id)s,
    kind = %(kind)s,
    status = %(status)s,
    attempts = %(attempts)s,
    error_code = %(error_code)s,
    created_at = %(created_at)s
WHERE organization_id = %(organization_id)s AND id = %(id)s;
