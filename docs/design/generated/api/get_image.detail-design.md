<!-- 実装から生成。直接編集しない。入力SHA256: e3cb305ddf380bd9917bab7f5404c8ac54c8511b8d91b58e7192aa0d5991c3cf -->

# 現在の認可で画像を配信 — detail-design

目的: 現在の認可で画像を配信。

入力はinterface帳票の型制約に従います。認可はサーバーの有効所属と権限から決まります。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## DB操作と入出力

| query | DB対象 | 処理 |
| --- | --- | --- |
| assets_get | assets | SELECT |
| departments_list | departments | SELECT |
| documents_get | documents | SELECT |
| memberships_list | memberships | SELECT |
| organizations_get | organizations | SELECT |
| users_list | users | SELECT |
| versions_get | versions | SELECT |

## 前提・正常／異常分岐

| 実装箇所 | 検査条件 | 不成立時／分岐 | HTTP |
| --- | --- | --- | --- |
| backend/src/kotorelay/context.py:40 | bool(organizations) and (not organizations[0].suspended) | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:43 | len(users) == 1 | 'unauthenticated' | 401 |
| backend/src/kotorelay/context.py:70 | doc.status != 'active' or not self.memberships | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:72 | doc.visibility == 'organization' | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:74 | self.member(doc.department_id) | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:82 | bool(rows) | not_found | 404 |
| backend/src/kotorelay/context.py:89 | allowed | not_found | 404 |
| backend/src/kotorelay/context.py:60 | m.department_id == department_id | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:96 | not self.permission(doc.department_id, 'draft') | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/context.py:94 | bool(rows) and rows[0].document_id == doc.id | not_found | 404 |
| backend/src/kotorelay/context.py:98 | digest(version.manifest.encode()) == version.manifest_hash | 'integrity' | 503 |
| backend/src/kotorelay/context.py:97 | self.can_read(doc) and doc.latest_version_id == version.id | not_found | 404 |
| backend/src/kotorelay/errors.py:13 | not condition | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/images/functions.py:146 | version_id is None | then / else の実装分岐 | 制御フロー参照 |
| backend/src/kotorelay/operations/images/functions.py:144 | bool(assets) | not_found | 404 |
| backend/src/kotorelay/operations/images/functions.py:150 | bool(docs) and docs[0].status != 'deleted' | not_found | 404 |
| backend/src/kotorelay/operations/images/functions.py:152 | ctx.can_read(doc) or ctx.permission(doc.department_id, 'draft') | not_found | 404 |
| backend/src/kotorelay/operations/images/functions.py:155 | any((i.placement.asset_id == asset.id and i.image_hash == asset.sha256 for i in manifest.images)) | not_found | 404 |

## 応答項目の取得元

| 実装箇所 | 返却式（DB行・変換結果・固定値） |
| --- | --- |
| backend/src/kotorelay/context.py:76 | doc.visibility == 'selected' and any((self.member(department) for department in json.loads(doc.shared_departments))) |
| backend/src/kotorelay/context.py:71 | False |
| backend/src/kotorelay/context.py:73 | True |
| backend/src/kotorelay/context.py:75 | True |
| backend/src/kotorelay/context.py:90 | doc |
| backend/src/kotorelay/context.py:67 | False |
| backend/src/kotorelay/context.py:61 | {'author': m.can_author, 'review': m.can_review, 'manage': m.leader, 'draft': m.can_author or m.can_review}.get(operation, False) |
| backend/src/kotorelay/context.py:100 | version |
| backend/src/kotorelay/generated/queries.py:542 | db.query('operations/images/sql/assets_get.sql', {'organization_id': organization_id, 'id': id}, AssetsRow) |
| backend/src/kotorelay/generated/queries.py:426 | db.query('operations/groups/sql/departments_list.sql', {'organization_id': organization_id}, DepartmentsRow) |
| backend/src/kotorelay/generated/queries.py:320 | db.query('operations/documents/sql/documents_get.sql', {'organization_id': organization_id, 'id': id}, DocumentsRow) |
| backend/src/kotorelay/generated/queries.py:462 | db.query('operations/groups/sql/memberships_list.sql', {'organization_id': organization_id}, MembershipsRow) |
| backend/src/kotorelay/generated/queries.py:481 | db.query('operations/identity/sql/organizations_get.sql', {'organization_id': organization_id, 'id': id}, OrganizationsRow) |
| backend/src/kotorelay/generated/queries.py:523 | db.query('operations/identity/sql/users_list.sql', {'organization_id': organization_id}, UsersRow) |
| backend/src/kotorelay/generated/queries.py:389 | db.query('operations/documents/sql/versions_get.sql', {'organization_id': organization_id, 'id': id}, VersionsRow) |
| backend/src/kotorelay/objects.py:17 | hashlib.sha256(data).hexdigest() |
| backend/src/kotorelay/operations/images/functions.py:161 | asset |
| backend/src/kotorelay/operations/images/functions.py:166 | ctx.objects.get(asset.object_key, asset.sha256) |
| backend/src/kotorelay/operations/images/router.py:32 | Response(f.image(ctx, str(asset_id), str(version_id) if version_id else None), media_type='image/png') |

異常時: DB transactionがrollbackします。S3の内容ハッシュ実体は孤立し得るため、公開認可に使わず、保持期間後の削除処理で回収します。外部配送失敗はoutboxのerror_codeとattemptsへ記録します。