-- ocr_runsを組織境界内でlistする。
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
