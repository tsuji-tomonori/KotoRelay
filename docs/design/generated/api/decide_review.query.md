<!-- 実装から生成。直接編集しない。入力SHA256: 8ddb6b8d66f674570acb431243c0b3f3887134895acc19f3980f35e395ebe090 -->

# manifestを確認して承認・却下 — query

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

## documents_update

正本: `backend/src/kotorelay/operations/documents/sql/documents_update.sql`

```sql
/* documentsを組織境界内でupdateする。 */
UPDATE documents SET department_id = %(department_id)s, title = %(title)s, created_by = %(created_by)s, visibility = %(visibility)s, shared_departments = %(shared_departments)s, status = %(status)s, revision = %(revision)s, next_version = %(next_version)s, latest_version_id = %(latest_version_id)s, updated_at = %(updated_at)s
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| row: DocumentsRow | DocumentsRow |

戻り値: `int`

## idempotency_get

正本: `backend/src/kotorelay/operations/system/sql/idempotency_get.sql`

```sql
/* idempotencyを組織境界内でgetする。 */
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

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |
| id: str | str |

戻り値: `list[IdempotencyRow]`

## idempotency_insert

正本: `backend/src/kotorelay/operations/system/sql/idempotency_insert.sql`

```sql
/* idempotencyを組織境界内でinsertする。 */
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

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| row: IdempotencyRow | IdempotencyRow |

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

## outbox_insert

正本: `backend/src/kotorelay/operations/indexing/sql/outbox_insert.sql`

```sql
/* outboxを組織境界内でinsertする。 */
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

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| row: OutboxRow | OutboxRow |

戻り値: `int`

## submissions_get

正本: `backend/src/kotorelay/operations/reviews/sql/submissions_get.sql`

```sql
/* submissionsを組織境界内でgetする。 */
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

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |
| id: str | str |

戻り値: `list[SubmissionsRow]`

## submissions_update

正本: `backend/src/kotorelay/operations/reviews/sql/submissions_update.sql`

```sql
/* submissionsを組織境界内でupdateする。 */
UPDATE submissions SET document_id = %(document_id)s, version_id = %(version_id)s, requested_by = %(requested_by)s, status = %(status)s, manifest_hash = %(manifest_hash)s, decided_by = %(decided_by)s, reason = %(reason)s, created_at = %(created_at)s, decided_at = %(decided_at)s
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| row: SubmissionsRow | SubmissionsRow |

戻り値: `int`

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

## versions_get

正本: `backend/src/kotorelay/operations/documents/sql/versions_get.sql`

```sql
/* versionsを組織境界内でgetする。 */
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

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |
| id: str | str |

戻り値: `list[VersionsRow]`
