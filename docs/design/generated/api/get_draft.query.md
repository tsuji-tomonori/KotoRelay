<!-- 実装から生成。直接編集しない。入力SHA256: f4209c4ed7b292c6ed57aa300cf25000f8931a1f59b1fb43cfeb436b1d949dbe -->

# 下書きを取得 — query

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

## documents_get

正本: `backend/src/kotorelay/operations/documents/sql/documents_get.sql`

```sql
/* documentsを組織境界内でgetする。 */
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

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |
| id: str | str |

戻り値: `list[DocumentsRow]`

## drafts_list

正本: `backend/src/kotorelay/operations/documents/sql/drafts_list.sql`

```sql
/* draftsを組織境界内でlistする。 */
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

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |

戻り値: `list[DraftsRow]`

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
