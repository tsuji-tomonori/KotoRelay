-- 認可判定と並行する失効操作を、同じ組織行へのOCCで直列化する。
UPDATE organizations SET revision = revision + 1
WHERE organization_id = %(organization_id)s AND id = %(id)s AND revision = %(revision)s;
