<!-- 実装から生成。直接編集しない。入力SHA256: 065f3a0aaa159ee25b4b54797ae13bebd5e0deb08cdd00f2becc4afbe26e1319 -->

# 現行認可で会話履歴を再表示 — クエリ

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## chat/chat_history/001_answers_list.sql

正本: `backend/src/kotorelay/operations/chat/chat_history/sql/001_answers_list.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する回答履歴を識別子順に一覧取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | answers | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | AnswersListParams |
| params.organization_id | str |


### 戻り値

型: `list[AnswersListRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| conversation_id | str |
| user_id | str |
| department_id | str |
| question_key | str |
| answer_key | str |
| evidence | str |
| status | str |
| model | str |
| created_at | datetime |


### 条件

WHERE organization_id = %(organization_id)s

ORDER BY id

```sql
/* 現在の組織に属する回答履歴を識別子順に一覧取得する。 */
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

## chat/chat_history/002_conversations_get.sql

正本: `backend/src/kotorelay/operations/chat/chat_history/sql/002_conversations_get.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する指定の会話について、会話の所有者と開始日時を取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | conversations | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | ConversationsGetParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `list[ConversationsGetRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| user_id | str |
| created_at | datetime |


### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の会話について、会話の所有者と開始日時を取得する。 */
SELECT
  id,
  organization_id,
  user_id,
  created_at
FROM conversations
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## chat/shared/001_assets_get.sql

正本: `backend/src/kotorelay/operations/chat/shared/sql/001_assets_get.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | assets | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | AssetsGetParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `list[AssetsGetRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| document_id | str |
| object_key | str |
| sha256 | str |
| media_type | str |
| width | int |
| height | int |
| size | int |
| created_at | datetime |


### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。 */
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

## chat/shared/002_chunks_get.sql

正本: `backend/src/kotorelay/operations/chat/shared/sql/002_chunks_get.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | chunks | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | ChunksGetParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `list[ChunksGetRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| document_id | str |
| version_id | str |
| body_key | str |
| sha256 | str |
| heading | str |
| placements | str |
| manifest_hash | str |
| ready | bool |


### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を取得する。 */
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

## chat/shared/003_documents_get.sql

正本: `backend/src/kotorelay/operations/chat/shared/sql/003_documents_get.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | documents | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | DocumentsGetParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `list[DocumentsGetRow]`

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

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。 */
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

## chat/shared/004_ocr_runs_get.sql

正本: `backend/src/kotorelay/operations/chat/shared/sql/004_ocr_runs_get.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | ocr_runs | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | OcrRunsGetParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `list[OcrRunsGetRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| document_id | str |
| asset_id | str |
| result_key | str |
| result_hash | str |
| engine | str |
| status | str |
| confirmed | bool |
| created_at | datetime |


### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。 */
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

## chat/shared/005_versions_get.sql

正本: `backend/src/kotorelay/operations/chat/shared/sql/005_versions_get.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | versions | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | VersionsGetParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `list[VersionsGetRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| document_id | str |
| number | int |
| title | str |
| body_key | str |
| body_hash | str |
| manifest | str |
| manifest_hash | str |
| created_by | str |
| created_at | datetime |


### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。 */
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