<!-- 実装から生成。直接編集しない。入力SHA256: 8ddb6b8d66f674570acb431243c0b3f3887134895acc19f3980f35e395ebe090 -->

# 本人と現在の所属権限を取得 — query

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

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
