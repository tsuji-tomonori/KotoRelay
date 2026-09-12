<!-- 実装から生成。直接編集しない。入力SHA256: 31de213f242d3d7bf0d4f5957d4ef327aaacb2267a973d8e0adce1f1531ac7e1 -->

# 版を確定して承認申請 — クエリ

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## assets_get.sql

正本: `backend/src/kotorelay/operations/images/sql/assets_get.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | assets | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |
| id | str |


### 戻り値

型: `list[AssetsRow]`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。 */
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
  organization_id = %(organization_id)s AND id = %(id)s
```

## audit_insert.sql

正本: `backend/src/kotorelay/operations/system/sql/audit_insert.sql`

### SQL種別

INSERT

### SQLの概要

現在の組織の監査記録として、操作した利用者・対象・変更前後の状態・理由を登録する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | audit | C |


### 引数

| 引数 | 型 |
| --- | --- |
| row | AuditRow |


### 戻り値

型: `int`

### 条件

SQL内にWHERE/JOIN/ORDER/LIMIT条件はありません。

```sql
/* 現在の組織の監査記録として、操作した利用者・対象・変更前後の状態・理由を登録する。 */
INSERT INTO audit (
  id,
  organization_id,
  user_id,
  document_id,
  version_id,
  action,
  before_state,
  after_state,
  reason,
  created_at
)
VALUES
  (
    %(id)s,
    %(organization_id)s,
    %(user_id)s,
    %(document_id)s,
    %(version_id)s,
    %(action)s,
    %(before_state)s,
    %(after_state)s,
    %(reason)s,
    %(created_at)s
  )
```

## departments_list.sql

正本: `backend/src/kotorelay/operations/groups/sql/departments_list.sql`

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
| organization_id | str |


### 戻り値

型: `list[DepartmentsRow]`

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

## documents_get.sql

正本: `backend/src/kotorelay/operations/documents/sql/documents_get.sql`

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
| organization_id | str |
| id | str |


### 戻り値

型: `list[DocumentsRow]`

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

## documents_update.sql

正本: `backend/src/kotorelay/operations/documents/sql/documents_update.sql`

### SQL種別

UPDATE

### SQLの概要

現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | documents | U |


### 引数

| 引数 | 型 |
| --- | --- |
| row | DocumentsRow |


### 戻り値

型: `int`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。 */
UPDATE documents SET department_id = %(department_id)s, title = %(title)s, created_by = %(created_by)s, visibility = %(visibility)s, shared_departments = %(shared_departments)s, status = %(status)s, revision = %(revision)s, next_version = %(next_version)s, latest_version_id = %(latest_version_id)s, updated_at = %(updated_at)s
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## drafts_list.sql

正本: `backend/src/kotorelay/operations/documents/sql/drafts_list.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する下書きを識別子順に一覧取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | drafts | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |


### 戻り値

型: `list[DraftsRow]`

### 条件

WHERE organization_id = %(organization_id)s

ORDER BY id

```sql
/* 現在の組織に属する下書きを識別子順に一覧取得する。 */
SELECT
  id,
  organization_id,
  document_id,
  body_key,
  body_hash,
  placements,
  revision,
  updated_by
FROM drafts
WHERE
  organization_id = %(organization_id)s
ORDER BY
  id
```

## idempotency_get.sql

正本: `backend/src/kotorelay/operations/system/sql/idempotency_get.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する指定の再送判定の記録について、実行済み操作の入力ハッシュと応答を取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | idempotency | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |
| id | str |


### 戻り値

型: `list[IdempotencyRow]`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の再送判定の記録について、実行済み操作の入力ハッシュと応答を取得する。 */
SELECT
  id,
  organization_id,
  user_id,
  operation,
  request_hash,
  response
FROM idempotency
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## idempotency_insert.sql

正本: `backend/src/kotorelay/operations/system/sql/idempotency_insert.sql`

### SQL種別

INSERT

### SQLの概要

現在の組織の操作の再送を判定するため、実行済み操作の入力ハッシュと応答を登録する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | idempotency | C |


### 引数

| 引数 | 型 |
| --- | --- |
| row | IdempotencyRow |


### 戻り値

型: `int`

### 条件

SQL内にWHERE/JOIN/ORDER/LIMIT条件はありません。

```sql
/* 現在の組織の操作の再送を判定するため、実行済み操作の入力ハッシュと応答を登録する。 */
INSERT INTO idempotency (
  id,
  organization_id,
  user_id,
  operation,
  request_hash,
  response
)
VALUES
  (
    %(id)s,
    %(organization_id)s,
    %(user_id)s,
    %(operation)s,
    %(request_hash)s,
    %(response)s
  )
```

## memberships_list.sql

正本: `backend/src/kotorelay/operations/groups/sql/memberships_list.sql`

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
| organization_id | str |


### 戻り値

型: `list[MembershipsRow]`

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

## ocr_runs_get.sql

正本: `backend/src/kotorelay/operations/images/sql/ocr_runs_get.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | ocr_runs | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |
| id | str |


### 戻り値

型: `list[OcrRunsRow]`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。 */
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
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## organizations_fence.sql

正本: `backend/src/kotorelay/operations/identity/sql/organizations_fence.sql`

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
| row | OrganizationsRow |


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

## organizations_get.sql

正本: `backend/src/kotorelay/operations/identity/sql/organizations_get.sql`

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
| organization_id | str |
| id | str |


### 戻り値

型: `list[OrganizationsRow]`

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

## submissions_insert.sql

正本: `backend/src/kotorelay/operations/reviews/sql/submissions_insert.sql`

### SQL種別

INSERT

### SQLの概要

現在の組織の承認申請を、対象の文書版・申請者・審査状態・検証用ハッシュとともに登録する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | submissions | C |


### 引数

| 引数 | 型 |
| --- | --- |
| row | SubmissionsRow |


### 戻り値

型: `int`

### 条件

SQL内にWHERE/JOIN/ORDER/LIMIT条件はありません。

```sql
/* 現在の組織の承認申請を、対象の文書版・申請者・審査状態・検証用ハッシュとともに登録する。 */
INSERT INTO submissions (
  id,
  organization_id,
  document_id,
  version_id,
  requested_by,
  status,
  manifest_hash,
  decided_by,
  reason,
  created_at,
  decided_at
)
VALUES
  (
    %(id)s,
    %(organization_id)s,
    %(document_id)s,
    %(version_id)s,
    %(requested_by)s,
    %(status)s,
    %(manifest_hash)s,
    %(decided_by)s,
    %(reason)s,
    %(created_at)s,
    %(decided_at)s
  )
```

## users_list.sql

正本: `backend/src/kotorelay/operations/identity/sql/users_list.sql`

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
| organization_id | str |


### 戻り値

型: `list[UsersRow]`

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

## versions_insert.sql

正本: `backend/src/kotorelay/operations/documents/sql/versions_insert.sql`

### SQL種別

INSERT

### SQLの概要

現在の組織の文書版を、版番号・本文の保存先・画像構成・検証用ハッシュを指定して登録する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | versions | C |


### 引数

| 引数 | 型 |
| --- | --- |
| row | VersionsRow |


### 戻り値

型: `int`

### 条件

SQL内にWHERE/JOIN/ORDER/LIMIT条件はありません。

```sql
/* 現在の組織の文書版を、版番号・本文の保存先・画像構成・検証用ハッシュを指定して登録する。 */
INSERT INTO versions (
  id,
  organization_id,
  document_id,
  number,
  title,
  body_key,
  body_hash,
  manifest,
  manifest_hash,
  created_by,
  created_at
)
VALUES
  (
    %(id)s,
    %(organization_id)s,
    %(document_id)s,
    %(number)s,
    %(title)s,
    %(body_key)s,
    %(body_hash)s,
    %(manifest)s,
    %(manifest_hash)s,
    %(created_by)s,
    %(created_at)s
  )
```