<!-- 実装から生成。直接編集しない。入力SHA256: f4209c4ed7b292c6ed57aa300cf25000f8931a1f59b1fb43cfeb436b1d949dbe -->

# 部署の所属権限を変更 — query

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## audit_insert

正本: `backend/src/kotorelay/operations/system/sql/audit_insert.sql`

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

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| row: AuditRow | AuditRow |

戻り値: `int`

## departments_get

正本: `backend/src/kotorelay/operations/groups/sql/departments_get.sql`

```sql
/* departmentsを組織境界内でgetする。 */
SELECT
  id,
  organization_id,
  name,
  active
FROM departments
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |
| id: str | str |

戻り値: `list[DepartmentsRow]`

## departments_list

正本: `backend/src/kotorelay/operations/groups/sql/departments_list.sql`

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

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |

戻り値: `list[DepartmentsRow]`

## memberships_insert

正本: `backend/src/kotorelay/operations/groups/sql/memberships_insert.sql`

```sql
/* membershipsを組織境界内でinsertする。 */
INSERT INTO memberships (
  id,
  organization_id,
  department_id,
  user_id,
  leader,
  can_author,
  can_review,
  active
)
VALUES
  (
    %(id)s,
    %(organization_id)s,
    %(department_id)s,
    %(user_id)s,
    %(leader)s,
    %(can_author)s,
    %(can_review)s,
    %(active)s
  )
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| row: MembershipsRow | MembershipsRow |

戻り値: `int`

## memberships_list

正本: `backend/src/kotorelay/operations/groups/sql/memberships_list.sql`

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

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |

戻り値: `list[MembershipsRow]`

## memberships_update

正本: `backend/src/kotorelay/operations/groups/sql/memberships_update.sql`

```sql
/* membershipsを組織境界内でupdateする。 */
UPDATE memberships SET department_id = %(department_id)s, user_id = %(user_id)s, leader = %(leader)s, can_author = %(can_author)s, can_review = %(can_review)s, active = %(active)s
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| row: MembershipsRow | MembershipsRow |

戻り値: `int`

## organizations_fence

正本: `backend/src/kotorelay/operations/identity/sql/organizations_fence.sql`

```sql
/* 認可判定と並行する失効操作を、同じ組織行へのOCCで直列化する。 */
UPDATE organizations SET revision = revision + 1
WHERE
  organization_id = %(organization_id)s AND id = %(id)s AND revision = %(revision)s
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| row: OrganizationsRow | OrganizationsRow |

戻り値: `int`

## organizations_get

正本: `backend/src/kotorelay/operations/identity/sql/organizations_get.sql`

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

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |
| id: str | str |

戻り値: `list[OrganizationsRow]`

## users_get

正本: `backend/src/kotorelay/operations/identity/sql/users_get.sql`

```sql
/* usersを組織境界内でgetする。 */
SELECT
  id,
  organization_id,
  subject,
  display_name,
  active,
  operator
FROM users
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |
| id: str | str |

戻り値: `list[UsersRow]`

## users_list

正本: `backend/src/kotorelay/operations/identity/sql/users_list.sql`

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

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |

戻り値: `list[UsersRow]`
