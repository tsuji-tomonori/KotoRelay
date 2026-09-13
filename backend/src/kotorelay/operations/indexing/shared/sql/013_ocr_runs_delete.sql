-- 現在の組織に属する指定の文字認識の実行記録の記録を削除する。
DELETE FROM ocr_runs
WHERE organization_id = %(organization_id)s AND id = %(id)s;
