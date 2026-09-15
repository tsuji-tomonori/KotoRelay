<!-- 実装から生成。直接編集しない。入力SHA256: f473ec4902a9e7cc973e702d4fbb05a99ce8c26a324da9a1f4592aab94dbd60c -->

# manifestを確認して承認・却下 — クエリ

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## reviews/decide_review/001_documents_update.sql

正本: `backend/src/kotorelay/operations/reviews/decide_review/sql/001_documents_update.sql`

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

## reviews/decide_review/002_outbox_insert.sql

正本: `backend/src/kotorelay/operations/reviews/decide_review/sql/002_outbox_insert.sql`

### SQL種別

INSERT

### SQLの概要

現在の組織の反映・削除ジョブを、対象文書と版・処理種別を指定して登録する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | outbox | C |


### 引数

| 引数 | 型 |
| --- | --- |
| params | OutboxInsertParams |
| params.id | str |
| params.organization_id | str |
| params.document_id | str |
| params.version_id | str &#124; None |
| params.kind | str |
| params.status | str |
| params.attempts | int |
| params.error_code | str |
| params.created_at | datetime |


### 戻り値

型: `int`

### 条件

SQL内にWHERE/JOIN/ORDER/LIMIT条件はありません。

```sql
/* 現在の組織の反映・削除ジョブを、対象文書と版・処理種別を指定して登録する。 */
INSERT INTO outbox (
  id,
  organization_id,
  document_id,
  version_id,
  kind,
  status,
  attempts,
  error_code,
  created_at
)
VALUES
  (
    %(id)s,
    %(organization_id)s,
    %(document_id)s,
    %(version_id)s,
    %(kind)s,
    %(status)s,
    %(attempts)s,
    %(error_code)s,
    %(created_at)s
  )
```

## reviews/decide_review/003_submissions_get.sql

正本: `backend/src/kotorelay/operations/reviews/decide_review/sql/003_submissions_get.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | submissions | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | SubmissionsGetParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `list[SubmissionsGetRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| document_id | str |
| version_id | str |
| requested_by | str |
| status | str |
| manifest_hash | str |
| decided_by | str &#124; None |
| reason | str |
| created_at | datetime |
| decided_at | datetime &#124; None |


### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を取得する。 */
SELECT
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
FROM submissions
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## reviews/decide_review/004_submissions_update.sql

正本: `backend/src/kotorelay/operations/reviews/decide_review/sql/004_submissions_update.sql`

### SQL種別

UPDATE

### SQLの概要

現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を更新する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | submissions | U |


### 引数

| 引数 | 型 |
| --- | --- |
| params | SubmissionsUpdateParams |
| params.document_id | str |
| params.version_id | str |
| params.requested_by | str |
| params.status | str |
| params.manifest_hash | str |
| params.decided_by | str &#124; None |
| params.reason | str |
| params.created_at | datetime |
| params.decided_at | datetime &#124; None |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `int`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を更新する。 */
UPDATE submissions SET document_id = %(document_id)s, version_id = %(version_id)s, requested_by = %(requested_by)s, status = %(status)s, manifest_hash = %(manifest_hash)s, decided_by = %(decided_by)s, reason = %(reason)s, created_at = %(created_at)s, decided_at = %(decided_at)s
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## reviews/decide_review/005_versions_get.sql

正本: `backend/src/kotorelay/operations/reviews/decide_review/sql/005_versions_get.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | versions | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | VersionsGetParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `list[VersionsGetRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| document_id | str |
| number | int |
| title | str |
| body_key | str |
| body_hash | str |
| manifest | str |
| manifest_hash | str |
| created_by | str |
| created_at | datetime |


### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。 */
SELECT
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
FROM versions
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
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

## system/authorization/010_versions_get.sql

正本: `backend/src/kotorelay/operations/system/authorization/sql/010_versions_get.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | versions | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | VersionsGetParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `list[VersionsGetRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| document_id | str |
| number | int |
| title | str |
| body_key | str |
| body_hash | str |
| manifest | str |
| manifest_hash | str |
| created_by | str |
| created_at | datetime |


### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。 */
SELECT
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
FROM versions
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```