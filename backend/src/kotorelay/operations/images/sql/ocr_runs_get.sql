-- ocr_runsを組織境界内でgetする。
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
WHERE organization_id = %(organization_id)s AND id = %(id)s;
