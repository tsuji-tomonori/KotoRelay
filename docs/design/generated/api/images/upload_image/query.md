<!-- 実装から生成。直接編集しない。入力SHA256: ac3b8a89c10fb6f4c0a9456ea4fb59251414105722d4188a0beaca0d8b493f26 -->

# 画像を添付して位置付きOCRを実行 — クエリ

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## images/upload_image/001_assets_insert.sql

正本: `backend/src/kotorelay/operations/images/upload_image/sql/001_assets_insert.sql`

### SQL種別

INSERT

### SQLの概要

現在の組織の文書に添付した画像の保存先・形式・寸法・検証用ハッシュを登録する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | assets | C |


### 引数

| 引数 | 型 |
| --- | --- |
| params | AssetsInsertParams |
| params.id | str |
| params.organization_id | str |
| params.document_id | str |
| params.object_key | str |
| params.sha256 | str |
| params.media_type | str |
| params.width | int |
| params.height | int |
| params.size | int |
| params.created_at | datetime |


### 戻り値

型: `int`

### 条件

SQL内にWHERE/JOIN/ORDER/LIMIT条件はありません。

```sql
/* 現在の組織の文書に添付した画像の保存先・形式・寸法・検証用ハッシュを登録する。 */
INSERT INTO assets (
  id,
  organization_id,
  document_id,
  object_key,
  sha256,
  media_type,
  width,
  height,
  size,
  created_at
)
VALUES
  (
    %(id)s,
    %(organization_id)s,
    %(document_id)s,
    %(object_key)s,
    %(sha256)s,
    %(media_type)s,
    %(width)s,
    %(height)s,
    %(size)s,
    %(created_at)s
  )
```

## images/upload_image/002_assets_list.sql

正本: `backend/src/kotorelay/operations/images/upload_image/sql/002_assets_list.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する添付画像を識別子順に一覧取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | assets | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | AssetsListParams |
| params.organization_id | str |


### 戻り値

型: `list[AssetsListRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| document_id | str |
| object_key | str |
| sha256 | str |
| media_type | str |
| width | int |
| height | int |
| size | int |
| created_at | datetime |


### 条件

WHERE organization_id = %(organization_id)s

ORDER BY id

```sql
/* 現在の組織に属する添付画像を識別子順に一覧取得する。 */
SELECT
  id,
  organization_id,
  document_id,
  object_key,
  sha256,
  media_type,
  width,
  height,
  size,
  created_at
FROM assets
WHERE
  organization_id = %(organization_id)s
ORDER BY
  id
```

## images/upload_image/003_ocr_runs_insert.sql

正本: `backend/src/kotorelay/operations/images/upload_image/sql/003_ocr_runs_insert.sql`

### SQL種別

INSERT

### SQLの概要

現在の組織の画像に対する文字認識の実行記録を、認識結果の保存先・検証用ハッシュ・確認状態とともに登録する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | ocr_runs | C |


### 引数

| 引数 | 型 |
| --- | --- |
| params | OcrRunsInsertParams |
| params.id | str |
| params.organization_id | str |
| params.document_id | str |
| params.asset_id | str |
| params.result_key | str |
| params.result_hash | str |
| params.engine | str |
| params.status | str |
| params.confirmed | bool |
| params.created_at | datetime |


### 戻り値

型: `int`

### 条件

SQL内にWHERE/JOIN/ORDER/LIMIT条件はありません。

```sql
/* 現在の組織の画像に対する文字認識の実行記録を、認識結果の保存先・検証用ハッシュ・確認状態とともに登録する。 */
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
)
VALUES
  (
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
  )
```

## system/authorization/002_departments_list.sql

正本: `backend/src/kotorelay/operations/system/authorization/sql/002_departments_list.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する部署を識別子順に一覧取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | departments | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | DepartmentsListParams |
| params.organization_id | str |


### 戻り値

型: `list[DepartmentsListRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| name | str |
| active | bool |


### 条件

WHERE organization_id = %(organization_id)s

ORDER BY id

```sql
/* 現在の組織に属する部署を識別子順に一覧取得する。 */
SELECT
  id,
  organization_id,
  name,
  active
FROM departments
WHERE
  organization_id = %(organization_id)s
ORDER BY
  id
```

## system/authorization/003_documents_get.sql

正本: `backend/src/kotorelay/operations/system/authorization/sql/003_documents_get.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | documents | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | DocumentsGetParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `list[DocumentsGetRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| department_id | str |
| title | str |
| created_by | str |
| visibility | str |
| shared_departments | str |
| status | str |
| revision | int |
| next_version | int |
| latest_version_id | str &#124; None |
| updated_at | datetime |


### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。 */
SELECT
  id,
  organization_id,
  department_id,
  title,
  created_by,
  visibility,
  shared_departments,
  status,
  revision,
  next_version,
  latest_version_id,
  updated_at
FROM documents
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## system/authorization/006_memberships_list.sql

正本: `backend/src/kotorelay/operations/system/authorization/sql/006_memberships_list.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する部署所属を識別子順に一覧取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | memberships | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | MembershipsListParams |
| params.organization_id | str |


### 戻り値

型: `list[MembershipsListRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| department_id | str |
| user_id | str |
| leader | bool |
| can_author | bool |
| can_review | bool |
| active | bool |


### 条件

WHERE organization_id = %(organization_id)s

ORDER BY id

```sql
/* 現在の組織に属する部署所属を識別子順に一覧取得する。 */
SELECT
  id,
  organization_id,
  department_id,
  user_id,
  leader,
  can_author,
  can_review,
  active
FROM memberships
WHERE
  organization_id = %(organization_id)s
ORDER BY
  id
```

## system/authorization/007_organizations_fence.sql

正本: `backend/src/kotorelay/operations/system/authorization/sql/007_organizations_fence.sql`

### SQL種別

UPDATE

### SQLの概要

組織の改訂番号が一致する場合だけ番号を進め、認可判定と権限失効の競合を検出する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | organizations | U |


### 引数

| 引数 | 型 |
| --- | --- |
| params | OrganizationsFenceParams |
| params.organization_id | str |
| params.id | str |
| params.revision | int |


### 戻り値

型: `int`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s AND revision = %(revision)s

```sql
/* 組織の改訂番号が一致する場合だけ番号を進め、認可判定と権限失効の競合を検出する。 */
UPDATE organizations SET revision = revision + 1
WHERE
  organization_id = %(organization_id)s AND id = %(id)s AND revision = %(revision)s
```

## system/authorization/008_organizations_get.sql

正本: `backend/src/kotorelay/operations/system/authorization/sql/008_organizations_get.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織の組織名・改訂番号・利用停止状態を取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | organizations | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | OrganizationsGetParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `list[OrganizationsGetRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| name | str |
| revision | int |
| suspended | bool |


### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織の組織名・改訂番号・利用停止状態を取得する。 */
SELECT
  id,
  organization_id,
  name,
  revision,
  suspended
FROM organizations
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## system/authorization/009_users_list.sql

正本: `backend/src/kotorelay/operations/system/authorization/sql/009_users_list.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する利用者を識別子順に一覧取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | users | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | UsersListParams |
| params.organization_id | str |


### 戻り値

型: `list[UsersListRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| subject | str |
| display_name | str |
| active | bool |
| operator | bool |


### 条件

WHERE organization_id = %(organization_id)s

ORDER BY id

```sql
/* 現在の組織に属する利用者を識別子順に一覧取得する。 */
SELECT
  id,
  organization_id,
  subject,
  display_name,
  active,
  operator
FROM users
WHERE
  organization_id = %(organization_id)s
ORDER BY
  id
```