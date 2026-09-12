<!-- 実装から生成。直接編集しない。入力SHA256: e3cb305ddf380bd9917bab7f5404c8ac54c8511b8d91b58e7192aa0d5991c3cf -->

# 画像を添付して位置付きOCRを実行 — detail-design

目的: 画像を添付して位置付きOCRを実行。

入力はinterface帳票の型制約に従います。認可はサーバーの有効所属と権限から決まります。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## DB操作と入出力

| query | DB対象 | 処理 |
| --- | --- | --- |
| assets_insert | assets | INSERT |
| assets_list | assets | SELECT |
| departments_list | departments | SELECT |
| documents_get | documents | SELECT |
| memberships_list | memberships | SELECT |
| ocr_runs_insert | ocr_runs | INSERT |
| organizations_fence | organizations | UPDATE |
| organizations_get | organizations | SELECT |
| users_list | users | SELECT |

## 前提・正常／異常分岐

| 実装箇所 | 検査条件 | 不成立時／分岐 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:40 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:43 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:82 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/context.py:89 | allowed | not_found | 404 |
| backend/src/kotorelay/context.py:53 | q.organizations_fence(self.db, self.organization) == 1 | 'conflict' | 409 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/images/functions.py:20 | 0 < len(data) <= max_bytes | 'invalid_image' | 422 |
| backend/src/kotorelay/operations/images/functions.py:23 | source.format in {'PNG', 'JPEG'} and source.width * source.height <= max_pixels | 'invalid_image' | 422 |
| backend/src/kotorelay/operations/images/functions.py:34 | len(value) <= max_bytes | 'invalid_image' | 422 |
| backend/src/kotorelay/operations/images/functions.py:56 | text | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/images/functions.py:74 | len(assets) < ctx.settings.max_document_images | 'limit' | 422 |

## 応答項目の取得元

| 実装箇所 | 返却式（DB行・変換結果・固定値） |
| --- | --- |
| backend/src/kotorelay/context.py:90 | doc |
| backend/src/kotorelay/context.py:22 | str(uuid4()) |
| backend/src/kotorelay/context.py:18 | datetime.now(UTC) |
| backend/src/kotorelay/generated/queries.py:551 | db.execute('operations/images/sql/assets_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:556 | db.query('operations/images/sql/assets_list.sql', {'organization_id': organization_id}, AssetsRow) |
| backend/src/kotorelay/generated/queries.py:426 | db.query('operations/groups/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/generated/queries.py:320 | db.query('operations/documents/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/generated/queries.py:462 | db.query('operations/groups/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/generated/queries.py:579 | db.execute('operations/images/sql/ocr_runs_insert.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:476 | db.execute('operations/identity/sql/organizations_fence.sql', row.model_dump()) |
| backend/src/kotorelay/generated/queries.py:481 | db.query('operations/identity/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/generated/queries.py:523 | db.query('operations/identity/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
| backend/src/kotorelay/operations/images/functions.py:35 | (value, image.width, image.height) |
| backend/src/kotorelay/operations/images/functions.py:68 | OcrResult(regions=regions, engine='tesseract-jpn-eng-v1', status='ready') |
| backend/src/kotorelay/operations/images/functions.py:52 | OcrResult(regions=[], engine='tesseract-jpn-eng-v1', status='failed') |
| backend/src/kotorelay/operations/images/functions.py:108 | {'asset': asset, 'ocr_run': run, 'ocr': result} |
| backend/src/kotorelay/operations/images/router.py:22 | f.upload(ctx, str(document_id), file.file.read(ctx.settings.max_image_bytes + 1)) |

異常時: DB transactionがrollbackします。S3の内容ハッシュ実体は孤立し得るため、公開認可に使わず、保持期間後の削除処理で回収します。外部配送失敗はoutboxのerror_codeとattemptsへ記録します。