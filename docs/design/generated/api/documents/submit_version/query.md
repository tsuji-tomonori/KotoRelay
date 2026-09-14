<!-- 実装から生成。直接編集しない。入力SHA256: ac3b8a89c10fb6f4c0a9456ea4fb59251414105722d4188a0beaca0d8b493f26 -->

# 版を確定して承認申請 — クエリ

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## documents/submit_version/001_assets_get.sql

正本: `backend/src/kotorelay/operations/documents/submit_version/sql/001_assets_get.sql`

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
| params | AssetsGetParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `list[AssetsGetRow]`

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

## documents/submit_version/002_documents_update.sql

正本: `backend/src/kotorelay/operations/documents/submit_version/sql/002_documents_update.sql`

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
| params | DocumentsUpdateParams |
| params.department_id | str |
| params.title | str |
| params.created_by | str |
| params.visibility | str |
| params.shared_departments | str |
| params.status | str |
| params.revision | int |
| params.next_version | int |
| params.latest_version_id | str &#124; None |
| params.updated_at | datetime |
| params.organization_id | str |
| params.id | str |


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

## documents/submit_version/003_drafts_list.sql

正本: `backend/src/kotorelay/operations/documents/submit_version/sql/003_drafts_list.sql`

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
| params | DraftsListParams |
| params.organization_id | str |


### 戻り値

型: `list[DraftsListRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| document_id | str |
| body_key | str |
| body_hash | str |
| placements | str |
| revision | int |
| updated_by | str |


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

## documents/submit_version/004_ocr_runs_get.sql

正本: `backend/src/kotorelay/operations/documents/submit_version/sql/004_ocr_runs_get.sql`

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
| params | OcrRunsGetParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `list[OcrRunsGetRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| document_id | str |
| asset_id | str |
| result_key | str |
| result_hash | str |
| engine | str |
| status | str |
| confirmed | bool |
| created_at | datetime |


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

## documents/submit_version/005_submissions_insert.sql

正本: `backend/src/kotorelay/operations/documents/submit_version/sql/005_submissions_insert.sql`

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
| params | SubmissionsInsertParams |
| params.id | str |
| params.organization_id | str |
| params.document_id | str |
| params.version_id | str |
| params.requested_by | str |
| params.status | str |
| params.manifest_hash | str |
| params.decided_by | str &#124; None |
| params.reason | str |
| params.created_at | datetime |
| params.decided_at | datetime &#124; None |


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

## documents/submit_version/006_versions_insert.sql

正本: `backend/src/kotorelay/operations/documents/submit_version/sql/006_versions_insert.sql`

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
| params | VersionsInsertParams |
| params.id | str |
| params.organization_id | str |
| params.document_id | str |
| params.number | int |
| params.title | str |
| params.body_key | str |
| params.body_hash | str |
| params.manifest | str |
| params.manifest_hash | str |
| params.created_by | str |
| params.created_at | datetime |


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

## system/authorization/001_audit_insert.sql

正本: `backend/src/kotorelay/operations/system/authorization/sql/001_audit_insert.sql`

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
| params | AuditInsertParams |
| params.id | str |
| params.organization_id | str |
| params.user_id | str |
| params.document_id | str &#124; None |
| params.version_id | str &#124; None |
| params.action | str |
| params.before_state | str |
| params.after_state | str |
| params.reason | str |
| params.created_at | datetime |


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

## system/authorization/004_idempotency_get.sql

正本: `backend/src/kotorelay/operations/system/authorization/sql/004_idempotency_get.sql`

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
| params | IdempotencyGetParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `list[IdempotencyGetRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| user_id | str |
| operation | str |
| request_hash | str |
| response | str |


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

## system/authorization/005_idempotency_insert.sql

正本: `backend/src/kotorelay/operations/system/authorization/sql/005_idempotency_insert.sql`

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
| params | IdempotencyInsertParams |
| params.id | str |
| params.organization_id | str |
| params.user_id | str |
| params.operation | str |
| params.request_hash | str |
| params.response | str |


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