<!-- 実装から生成。直接編集しない。入力SHA256: a4642be092686b22c6cb0bbcfdd011c0a0c93352fc1191e08d5c7dfccac4e973 -->

# 部署の利用数と文書貢献を集計 — クエリ

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## metrics/department_metrics/001_documents_list.sql

正本: `backend/src/kotorelay/operations/metrics/department_metrics/sql/001_documents_list.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する文書を識別子順に一覧取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | documents | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | DocumentsListParams |
| params.organization_id | str |


### 戻り値

型: `list[DocumentsListRow]`

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

WHERE organization_id = %(organization_id)s

ORDER BY id

```sql
/* 現在の組織に属する文書を識別子順に一覧取得する。 */
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
  organization_id = %(organization_id)s
ORDER BY
  id
```

## metrics/department_metrics/002_events_list.sql

正本: `backend/src/kotorelay/operations/metrics/department_metrics/sql/002_events_list.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する利用イベントを識別子順に一覧取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | events | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | EventsListParams |
| params.organization_id | str |


### 戻り値

型: `list[EventsListRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| user_id | str |
| department_id | str |
| document_id | str &#124; None |
| answer_id | str &#124; None |
| kind | str |
| outcome | str |
| created_at | datetime |


### 条件

WHERE organization_id = %(organization_id)s

ORDER BY id

```sql
/* 現在の組織に属する利用イベントを識別子順に一覧取得する。 */
SELECT
  id,
  organization_id,
  user_id,
  department_id,
  document_id,
  answer_id,
  kind,
  outcome,
  created_at
FROM events
WHERE
  organization_id = %(organization_id)s
ORDER BY
  id
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