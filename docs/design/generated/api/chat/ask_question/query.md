<!-- 実装から生成。直接編集しない。入力SHA256: 4c18ae62a9b9de513581947abfc60f1ec45b9f631019a142a812724b4695a84b -->

# 最新承認版の根拠で回答 — クエリ

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## answers_get.sql

正本: `backend/src/kotorelay/operations/chat/sql/answers_get.sql`

### SQL種別

SELECT

### SQLの概要

answersを組織境界内でgetする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | answers | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |
| id | str |


### 戻り値

型: `list[AnswersRow]`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* answersを組織境界内でgetする。 */
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
  organization_id = %(organization_id)s AND id = %(id)s
```

## answers_insert.sql

正本: `backend/src/kotorelay/operations/chat/sql/answers_insert.sql`

### SQL種別

INSERT

### SQLの概要

answersを組織境界内でinsertする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | answers | C |


### 引数

| 引数 | 型 |
| --- | --- |
| row | AnswersRow |


### 戻り値

型: `int`

### 条件

SQL内にWHERE/JOIN/ORDER/LIMIT条件はありません。

```sql
/* answersを組織境界内でinsertする。 */
INSERT INTO answers (
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
)
VALUES
  (
    %(id)s,
    %(organization_id)s,
    %(conversation_id)s,
    %(user_id)s,
    %(department_id)s,
    %(question_key)s,
    %(answer_key)s,
    %(evidence)s,
    %(status)s,
    %(model)s,
    %(created_at)s
  )
```

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

## chunks_get.sql

正本: `backend/src/kotorelay/operations/indexing/sql/chunks_get.sql`

### SQL種別

SELECT

### SQLの概要

chunksを組織境界内でgetする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | chunks | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |
| id | str |


### 戻り値

型: `list[ChunksRow]`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* chunksを組織境界内でgetする。 */
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
  organization_id = %(organization_id)s AND id = %(id)s
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

## conversations_get.sql

正本: `backend/src/kotorelay/operations/chat/sql/conversations_get.sql`

### SQL種別

SELECT

### SQLの概要

conversationsを組織境界内でgetする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | conversations | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |
| id | str |


### 戻り値

型: `list[ConversationsRow]`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* conversationsを組織境界内でgetする。 */
SELECT
  id,
  organization_id,
  user_id,
  created_at
FROM conversations
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## conversations_insert.sql

正本: `backend/src/kotorelay/operations/chat/sql/conversations_insert.sql`

### SQL種別

INSERT

### SQLの概要

conversationsを組織境界内でinsertする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | conversations | C |


### 引数

| 引数 | 型 |
| --- | --- |
| row | ConversationsRow |


### 戻り値

型: `int`

### 条件

SQL内にWHERE/JOIN/ORDER/LIMIT条件はありません。

```sql
/* conversationsを組織境界内でinsertする。 */
INSERT INTO conversations (
  id,
  organization_id,
  user_id,
  created_at
)
VALUES
  (%(id)s, %(organization_id)s, %(user_id)s, %(created_at)s)
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

## events_insert.sql

正本: `backend/src/kotorelay/operations/metrics/sql/events_insert.sql`

### SQL種別

INSERT

### SQLの概要

eventsを組織境界内でinsertする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | events | C |


### 引数

| 引数 | 型 |
| --- | --- |
| row | EventsRow |


### 戻り値

型: `int`

### 条件

SQL内にWHERE/JOIN/ORDER/LIMIT条件はありません。

```sql
/* eventsを組織境界内でinsertする。 */
INSERT INTO events (
  id,
  organization_id,
  user_id,
  department_id,
  document_id,
  answer_id,
  kind,
  outcome,
  created_at
)
VALUES
  (
    %(id)s,
    %(organization_id)s,
    %(user_id)s,
    %(department_id)s,
    %(document_id)s,
    %(answer_id)s,
    %(kind)s,
    %(outcome)s,
    %(created_at)s
  )
```

## events_list.sql

正本: `backend/src/kotorelay/operations/metrics/sql/events_list.sql`

### SQL種別

SELECT

### SQLの概要

eventsを組織境界内でlistする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | events | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |


### 戻り値

型: `list[EventsRow]`

### 条件

WHERE organization_id = %(organization_id)s

ORDER BY id

```sql
/* eventsを組織境界内でlistする。 */
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

## idempotency_get.sql

正本: `backend/src/kotorelay/operations/system/sql/idempotency_get.sql`

### SQL種別

SELECT

### SQLの概要

idempotencyを組織境界内でgetする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | idempotency | R |


### 引数

| 引数 | 型 |
| --- | --- |
| organization_id | str |
| id | str |


### 戻り値

型: `list[IdempotencyRow]`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

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

## idempotency_insert.sql

正本: `backend/src/kotorelay/operations/system/sql/idempotency_insert.sql`

### SQL種別

INSERT

### SQLの概要

idempotencyを組織境界内でinsertする。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | idempotency | C |


### 引数

| 引数 | 型 |
| --- | --- |
| row | IdempotencyRow |


### 戻り値

型: `int`

### 条件

SQL内にWHERE/JOIN/ORDER/LIMIT条件はありません。

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