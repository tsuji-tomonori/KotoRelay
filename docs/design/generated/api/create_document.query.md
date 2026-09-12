<!-- 実装から生成。直接編集しない。入力SHA256: 209f2912c47883d8fdc722aafdde6cf403dff105c2efced6770337a06a320dd2 -->

# 文書を作成 — query

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

## documents_insert

正本: `backend/src/kotorelay/operations/documents/sql/documents_insert.sql`

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

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| row: DocumentsRow | DocumentsRow |

戻り値: `int`

## drafts_insert

正本: `backend/src/kotorelay/operations/documents/sql/drafts_insert.sql`

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

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| row: DraftsRow | DraftsRow |

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
