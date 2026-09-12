-- 現在の組織の画像に対する文字認識の実行記録を、認識結果の保存先・検証用ハッシュ・確認状態とともに登録する。
INSERT INTO ocr_runs (
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
) VALUES (
    %(id)s,
    %(organization_id)s,
    %(document_id)s,
    %(asset_id)s,
    %(result_key)s,
    %(result_hash)s,
    %(engine)s,
    %(status)s,
    %(confirmed)s,
    %(created_at)s
);
