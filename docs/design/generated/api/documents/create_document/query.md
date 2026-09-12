<!-- 実装から生成。直接編集しない。入力SHA256: 4c18ae62a9b9de513581947abfc60f1ec45b9f631019a142a812724b4695a84b -->

# 文書を作成 — クエリ

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## audit_insert.sql

正本: `backend/src/kotorelay/operations/system/sql/audit_insert.sql`

### SQL種別

INSERT

### SQLの概要

auditを組織境界内でinsertする。

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
/* auditを組織境界内でinsertする。 */
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

departmentsを組織境界内でlistする。

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
/* departmentsを組織境界内でlistする。 */
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

## documents_insert.sql

正本: `backend/src/kotorelay/operations/documents/sql/documents_insert.sql`

### SQL種別

INSERT

### SQLの概要

documentsを組織境界内でinsertする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | documents | C |


### 引数

| 引数 | 型 |
| --- | --- |
| row | DocumentsRow |


### 戻り値

型: `int`

### 条件

SQL内にWHERE/JOIN/ORDER/LIMIT条件はありません。

```sql
/* documentsを組織境界内でinsertする。 */
INSERT INTO documents (
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
)
VALUES
  (
    %(id)s,
    %(organization_id)s,
    %(department_id)s,
    %(title)s,
    %(created_by)s,
    %(visibility)s,
    %(shared_departments)s,
    %(status)s,
    %(revision)s,
    %(next_version)s,
    %(latest_version_id)s,
    %(updated_at)s
  )
```

## drafts_insert.sql

正本: `backend/src/kotorelay/operations/documents/sql/drafts_insert.sql`

### SQL種別

INSERT

### SQLの概要

draftsを組織境界内でinsertする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | drafts | C |


### 引数

| 引数 | 型 |
| --- | --- |
| row | DraftsRow |


### 戻り値

型: `int`

### 条件

SQL内にWHERE/JOIN/ORDER/LIMIT条件はありません。

```sql
/* draftsを組織境界内でinsertする。 */
INSERT INTO drafts (
  id,
  organization_id,
  document_id,
  body_key,
  body_hash,
  placements,
  revision,
  updated_by
)
VALUES
  (
    %(id)s,
    %(organization_id)s,
    %(document_id)s,
    %(body_key)s,
    %(body_hash)s,
    %(placements)s,
    %(revision)s,
    %(updated_by)s
  )
```

## memberships_list.sql

正本: `backend/src/kotorelay/operations/groups/sql/memberships_list.sql`

### SQL種別

SELECT

### SQLの概要

membershipsを組織境界内でlistする。

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
/* membershipsを組織境界内でlistする。 */
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

## organizations_fence.sql

正本: `backend/src/kotorelay/operations/identity/sql/organizations_fence.sql`

### SQL種別

UPDATE

### SQLの概要

認可判定と並行する失効操作を、同じ組織行へのOCCで直列化する。

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
/* 認可判定と並行する失効操作を、同じ組織行へのOCCで直列化する。 */
UPDATE organizations SET revision = revision + 1
WHERE
  organization_id = %(organization_id)s AND id = %(id)s AND revision = %(revision)s
```

## organizations_get.sql

正本: `backend/src/kotorelay/operations/identity/sql/organizations_get.sql`

### SQL種別

SELECT

### SQLの概要

organizationsを組織境界内でgetする。

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
/* organizationsを組織境界内でgetする。 */
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

## users_list.sql

正本: `backend/src/kotorelay/operations/identity/sql/users_list.sql`

### SQL種別

SELECT

### SQLの概要

usersを組織境界内でlistする。

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
/* usersを組織境界内でlistする。 */
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