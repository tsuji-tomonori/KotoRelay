-- 組織の改訂番号が一致する場合だけ番号を進め、認可判定と権限失効の競合を検出する。
UPDATE organizations SET revision = revision + 1
WHERE organization_id = %(organization_id)s AND id = %(id)s AND revision = %(revision)s;
