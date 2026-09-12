-- ocr_runsを組織境界内でdeleteする。
DELETE FROM ocr_runs WHERE organization_id = %(organization_id)s AND id = %(id)s;
