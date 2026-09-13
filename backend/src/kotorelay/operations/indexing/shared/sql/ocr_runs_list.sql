-- 現在の組織に属する文字認識の実行記録を識別子順に一覧取得する。
SELECT
    id,
    organization_id,
    document_id,
    asset_id,
    result_key,
    result_hash,
    engine,
    status,
    confirmed,
    created_at
FROM ocr_runs
WHERE organization_id = %(organization_id)s
ORDER BY id;
