-- 現在の組織の反映・削除ジョブを、対象文書と版・処理種別を指定して登録する。
INSERT INTO outbox (
    id, organization_id, document_id, version_id, kind, status, attempts, error_code, created_at
) VALUES (
    %(id)s,
    %(organization_id)s,
    %(document_id)s,
    %(version_id)s,
    %(kind)s,
    %(status)s,
    %(attempts)s,
    %(error_code)s,
    %(created_at)s
);
