-- 現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。
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
