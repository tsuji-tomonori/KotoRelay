<!-- 実装から生成。直接編集しない。入力SHA256: 4c18ae62a9b9de513581947abfc60f1ec45b9f631019a142a812724b4695a84b -->

# 反映ジョブを再処理 — クエリ

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## answers_list.sql

正本: `backend/src/kotorelay/operations/chat/sql/answers_list.sql`

### SQL種別

SELECT

### SQLの概要

answersを組織境界内でlistする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | answers | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |


### 戻り値

型: `list[AnswersRow]`

### 条件

WHERE organization_id = %(organization_id)s

ORDER BY id

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

## assets_delete.sql

正本: `backend/src/kotorelay/operations/images/sql/assets_delete.sql`

### SQL種別

DELETE

### SQLの概要

assetsを組織境界内でdeleteする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | assets | D |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |
| id | str |


### 戻り値

型: `int`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* assetsを組織境界内でdeleteする。 */
DELETE FROM assets
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## assets_get.sql

正本: `backend/src/kotorelay/operations/images/sql/assets_get.sql`

### SQL種別

SELECT

### SQLの概要

assetsを組織境界内でgetする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | assets | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |
| id | str |


### 戻り値

型: `list[AssetsRow]`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

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

## assets_list.sql

正本: `backend/src/kotorelay/operations/images/sql/assets_list.sql`

### SQL種別

SELECT

### SQLの概要

assetsを組織境界内でlistする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | assets | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |


### 戻り値

型: `list[AssetsRow]`

### 条件

WHERE organization_id = %(organization_id)s

ORDER BY id

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

## chunks_delete.sql

正本: `backend/src/kotorelay/operations/indexing/sql/chunks_delete.sql`

### SQL種別

DELETE

### SQLの概要

chunksを組織境界内でdeleteする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | chunks | D |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |
| id | str |


### 戻り値

型: `int`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* chunksを組織境界内でdeleteする。 */
DELETE FROM chunks
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## chunks_insert.sql

正本: `backend/src/kotorelay/operations/indexing/sql/chunks_insert.sql`

### SQL種別

INSERT

### SQLの概要

chunksを組織境界内でinsertする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | chunks | C |


### 引数

| 引数 | 型 |
| --- | --- |
| row | ChunksRow |


### 戻り値

型: `int`

### 条件

SQL内にWHERE/JOIN/ORDER/LIMIT条件はありません。

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

## chunks_list.sql

正本: `backend/src/kotorelay/operations/indexing/sql/chunks_list.sql`

### SQL種別

SELECT

### SQLの概要

chunksを組織境界内でlistする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | chunks | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |


### 戻り値

型: `list[ChunksRow]`

### 条件

WHERE organization_id = %(organization_id)s

ORDER BY id

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

## chunks_update.sql

正本: `backend/src/kotorelay/operations/indexing/sql/chunks_update.sql`

### SQL種別

UPDATE

### SQLの概要

chunksを組織境界内でupdateする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | chunks | U |


### 引数

| 引数 | 型 |
| --- | --- |
| row | ChunksRow |


### 戻り値

型: `int`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* chunksを組織境界内でupdateする。 */
UPDATE chunks SET document_id = %(document_id)s, version_id = %(version_id)s, body_key = %(body_key)s, sha256 = %(sha256)s, heading = %(heading)s, placements = %(placements)s, manifest_hash = %(manifest_hash)s, ready = %(ready)s
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
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

## documents_get.sql

正本: `backend/src/kotorelay/operations/documents/sql/documents_get.sql`

### SQL種別

SELECT

### SQLの概要

documentsを組織境界内でgetする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | documents | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |
| id | str |


### 戻り値

型: `list[DocumentsRow]`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

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

## documents_list.sql

正本: `backend/src/kotorelay/operations/documents/sql/documents_list.sql`

### SQL種別

SELECT

### SQLの概要

documentsを組織境界内でlistする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | documents | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |


### 戻り値

型: `list[DocumentsRow]`

### 条件

WHERE organization_id = %(organization_id)s

ORDER BY id

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

## drafts_delete.sql

正本: `backend/src/kotorelay/operations/documents/sql/drafts_delete.sql`

### SQL種別

DELETE

### SQLの概要

draftsを組織境界内でdeleteする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | drafts | D |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |
| id | str |


### 戻り値

型: `int`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* draftsを組織境界内でdeleteする。 */
DELETE FROM drafts
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## drafts_list.sql

正本: `backend/src/kotorelay/operations/documents/sql/drafts_list.sql`

### SQL種別

SELECT

### SQLの概要

draftsを組織境界内でlistする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | drafts | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |


### 戻り値

型: `list[DraftsRow]`

### 条件

WHERE organization_id = %(organization_id)s

ORDER BY id

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

## ocr_runs_delete.sql

正本: `backend/src/kotorelay/operations/images/sql/ocr_runs_delete.sql`

### SQL種別

DELETE

### SQLの概要

ocr_runsを組織境界内でdeleteする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | ocr_runs | D |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |
| id | str |


### 戻り値

型: `int`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* ocr_runsを組織境界内でdeleteする。 */
DELETE FROM ocr_runs
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## ocr_runs_get.sql

正本: `backend/src/kotorelay/operations/images/sql/ocr_runs_get.sql`

### SQL種別

SELECT

### SQLの概要

ocr_runsを組織境界内でgetする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | ocr_runs | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |
| id | str |


### 戻り値

型: `list[OcrRunsRow]`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

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

## ocr_runs_list.sql

正本: `backend/src/kotorelay/operations/images/sql/ocr_runs_list.sql`

### SQL種別

SELECT

### SQLの概要

ocr_runsを組織境界内でlistする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | ocr_runs | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |


### 戻り値

型: `list[OcrRunsRow]`

### 条件

WHERE organization_id = %(organization_id)s

ORDER BY id

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

## outbox_get.sql

正本: `backend/src/kotorelay/operations/indexing/sql/outbox_get.sql`

### SQL種別

SELECT

### SQLの概要

outboxを組織境界内でgetする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | outbox | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |
| id | str |


### 戻り値

型: `list[OutboxRow]`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

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

## outbox_update.sql

正本: `backend/src/kotorelay/operations/indexing/sql/outbox_update.sql`

### SQL種別

UPDATE

### SQLの概要

outboxを組織境界内でupdateする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | outbox | U |


### 引数

| 引数 | 型 |
| --- | --- |
| row | OutboxRow |


### 戻り値

型: `int`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* outboxを組織境界内でupdateする。 */
UPDATE outbox SET document_id = %(document_id)s, version_id = %(version_id)s, kind = %(kind)s, status = %(status)s, attempts = %(attempts)s, error_code = %(error_code)s, created_at = %(created_at)s
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

## versions_get.sql

正本: `backend/src/kotorelay/operations/documents/sql/versions_get.sql`

### SQL種別

SELECT

### SQLの概要

versionsを組織境界内でgetする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | versions | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |
| id | str |


### 戻り値

型: `list[VersionsRow]`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

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

## versions_list.sql

正本: `backend/src/kotorelay/operations/documents/sql/versions_list.sql`

### SQL種別

SELECT

### SQLの概要

versionsを組織境界内でlistする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | versions | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |


### 戻り値

型: `list[VersionsRow]`

### 条件

WHERE organization_id = %(organization_id)s

ORDER BY id

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