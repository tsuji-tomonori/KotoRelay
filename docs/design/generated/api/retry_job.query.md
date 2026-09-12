<!-- 実装から生成。直接編集しない。入力SHA256: e3cb305ddf380bd9917bab7f5404c8ac54c8511b8d91b58e7192aa0d5991c3cf -->

# 反映ジョブを再処理 — query

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## answers_list

正本: `backend/src/kotorelay/operations/chat/sql/answers_list.sql`

```sql
/* answersを組織境界内でlistする。 */
SELECT
  id,
  organization_id,
  conversation_id,
  user_id,
  department_id,
  question_key,
  answer_key,
  evidence,
  status,
  model,
  created_at
FROM answers
WHERE
  organization_id = %(organization_id)s
ORDER BY
  id
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |

戻り値: `list[AnswersRow]`

## assets_delete

正本: `backend/src/kotorelay/operations/images/sql/assets_delete.sql`

```sql
/* assetsを組織境界内でdeleteする。 */
DELETE FROM assets
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |
| id: str | str |

戻り値: `int`

## assets_get

正本: `backend/src/kotorelay/operations/images/sql/assets_get.sql`

```sql
/* assetsを組織境界内でgetする。 */
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

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |
| id: str | str |

戻り値: `list[AssetsRow]`

## assets_list

正本: `backend/src/kotorelay/operations/images/sql/assets_list.sql`

```sql
/* assetsを組織境界内でlistする。 */
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
  organization_id = %(organization_id)s
ORDER BY
  id
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |

戻り値: `list[AssetsRow]`

## chunks_delete

正本: `backend/src/kotorelay/operations/indexing/sql/chunks_delete.sql`

```sql
/* chunksを組織境界内でdeleteする。 */
DELETE FROM chunks
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |
| id: str | str |

戻り値: `int`

## chunks_insert

正本: `backend/src/kotorelay/operations/indexing/sql/chunks_insert.sql`

```sql
/* chunksを組織境界内でinsertする。 */
INSERT INTO chunks (
  id,
  organization_id,
  document_id,
  version_id,
  body_key,
  sha256,
  heading,
  placements,
  manifest_hash,
  ready
)
VALUES
  (
    %(id)s,
    %(organization_id)s,
    %(document_id)s,
    %(version_id)s,
    %(body_key)s,
    %(sha256)s,
    %(heading)s,
    %(placements)s,
    %(manifest_hash)s,
    %(ready)s
  )
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| row: ChunksRow | ChunksRow |

戻り値: `int`

## chunks_list

正本: `backend/src/kotorelay/operations/indexing/sql/chunks_list.sql`

```sql
/* chunksを組織境界内でlistする。 */
SELECT
  id,
  organization_id,
  document_id,
  version_id,
  body_key,
  sha256,
  heading,
  placements,
  manifest_hash,
  ready
FROM chunks
WHERE
  organization_id = %(organization_id)s
ORDER BY
  id
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |

戻り値: `list[ChunksRow]`

## chunks_update

正本: `backend/src/kotorelay/operations/indexing/sql/chunks_update.sql`

```sql
/* chunksを組織境界内でupdateする。 */
UPDATE chunks SET document_id = %(document_id)s, version_id = %(version_id)s, body_key = %(body_key)s, sha256 = %(sha256)s, heading = %(heading)s, placements = %(placements)s, manifest_hash = %(manifest_hash)s, ready = %(ready)s
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| row: ChunksRow | ChunksRow |

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

## documents_list

正本: `backend/src/kotorelay/operations/documents/sql/documents_list.sql`

```sql
/* documentsを組織境界内でlistする。 */
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

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |

戻り値: `list[DocumentsRow]`

## drafts_delete

正本: `backend/src/kotorelay/operations/documents/sql/drafts_delete.sql`

```sql
/* draftsを組織境界内でdeleteする。 */
DELETE FROM drafts
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |
| id: str | str |

戻り値: `int`

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

## ocr_runs_delete

正本: `backend/src/kotorelay/operations/images/sql/ocr_runs_delete.sql`

```sql
/* ocr_runsを組織境界内でdeleteする。 */
DELETE FROM ocr_runs
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |
| id: str | str |

戻り値: `int`

## ocr_runs_get

正本: `backend/src/kotorelay/operations/images/sql/ocr_runs_get.sql`

```sql
/* ocr_runsを組織境界内でgetする。 */
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

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |
| id: str | str |

戻り値: `list[OcrRunsRow]`

## ocr_runs_list

正本: `backend/src/kotorelay/operations/images/sql/ocr_runs_list.sql`

```sql
/* ocr_runsを組織境界内でlistする。 */
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
  organization_id = %(organization_id)s
ORDER BY
  id
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |

戻り値: `list[OcrRunsRow]`

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

## outbox_get

正本: `backend/src/kotorelay/operations/indexing/sql/outbox_get.sql`

```sql
/* outboxを組織境界内でgetする。 */
SELECT
  id,
  organization_id,
  document_id,
  version_id,
  kind,
  status,
  attempts,
  error_code,
  created_at
FROM outbox
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |
| id: str | str |

戻り値: `list[OutboxRow]`

## outbox_update

正本: `backend/src/kotorelay/operations/indexing/sql/outbox_update.sql`

```sql
/* outboxを組織境界内でupdateする。 */
UPDATE outbox SET document_id = %(document_id)s, version_id = %(version_id)s, kind = %(kind)s, status = %(status)s, attempts = %(attempts)s, error_code = %(error_code)s, created_at = %(created_at)s
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| row: OutboxRow | OutboxRow |

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

## versions_list

正本: `backend/src/kotorelay/operations/documents/sql/versions_list.sql`

```sql
/* versionsを組織境界内でlistする。 */
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
  organization_id = %(organization_id)s
ORDER BY
  id
```

| 入力／出力型 | 定義 |
| --- | --- |
| db: Database | Database |
| organization_id: str | str |

戻り値: `list[VersionsRow]`
