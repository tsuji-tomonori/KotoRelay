<!-- 実装から生成。直接編集しない。入力SHA256: dc958b6e6841a9f29856eb932e8271e37a6d4416a3266624301c411c89949f81 -->

# 反映ジョブを再処理 — クエリ

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

## indexing/shared/001_answers_list.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/001_answers_list.sql`

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

## indexing/shared/002_assets_delete.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/002_assets_delete.sql`

### SQL種別

DELETE

### SQLの概要

現在の組織に属する指定の添付画像の記録を削除する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | assets | D |


### 引数

| 引数 | 型 |
| --- | --- |
| params | AssetsDeleteParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `int`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の添付画像の記録を削除する。 */
DELETE FROM assets
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## indexing/shared/003_assets_get.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/003_assets_get.sql`

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

## indexing/shared/004_assets_list.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/004_assets_list.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する添付画像を識別子順に一覧取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | assets | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | AssetsListParams |
| params.organization_id | str |


### 戻り値

型: `list[AssetsListRow]`

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

WHERE organization_id = %(organization_id)s

ORDER BY id

```sql
/* 現在の組織に属する添付画像を識別子順に一覧取得する。 */
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

## indexing/shared/005_chunks_delete.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/005_chunks_delete.sql`

### SQL種別

DELETE

### SQLの概要

現在の組織に属する指定の検索用の文書断片の記録を削除する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | chunks | D |


### 引数

| 引数 | 型 |
| --- | --- |
| params | ChunksDeleteParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `int`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の検索用の文書断片の記録を削除する。 */
DELETE FROM chunks
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## indexing/shared/006_chunks_insert.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/006_chunks_insert.sql`

### SQL種別

INSERT

### SQLの概要

現在の組織の検索用の文書断片を、出典の版・本文の保存先・画像配置とともに登録する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | chunks | C |


### 引数

| 引数 | 型 |
| --- | --- |
| params | ChunksInsertParams |
| params.id | str |
| params.organization_id | str |
| params.document_id | str |
| params.version_id | str |
| params.body_key | str |
| params.sha256 | str |
| params.heading | str |
| params.placements | str |
| params.manifest_hash | str |
| params.ready | bool |


### 戻り値

型: `int`

### 条件

SQL内にWHERE/JOIN/ORDER/LIMIT条件はありません。

```sql
/* 現在の組織の検索用の文書断片を、出典の版・本文の保存先・画像配置とともに登録する。 */
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

## indexing/shared/007_chunks_list.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/007_chunks_list.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する検索用の文書断片を識別子順に一覧取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | chunks | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | ChunksListParams |
| params.organization_id | str |


### 戻り値

型: `list[ChunksListRow]`

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

WHERE organization_id = %(organization_id)s

ORDER BY id

```sql
/* 現在の組織に属する検索用の文書断片を識別子順に一覧取得する。 */
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

## indexing/shared/008_chunks_update.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/008_chunks_update.sql`

### SQL種別

UPDATE

### SQLの概要

現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を更新する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | chunks | U |


### 引数

| 引数 | 型 |
| --- | --- |
| params | ChunksUpdateParams |
| params.document_id | str |
| params.version_id | str |
| params.body_key | str |
| params.sha256 | str |
| params.heading | str |
| params.placements | str |
| params.manifest_hash | str |
| params.ready | bool |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `int`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を更新する。 */
UPDATE chunks SET document_id = %(document_id)s, version_id = %(version_id)s, body_key = %(body_key)s, sha256 = %(sha256)s, heading = %(heading)s, placements = %(placements)s, manifest_hash = %(manifest_hash)s, ready = %(ready)s
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## indexing/shared/009_documents_get.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/009_documents_get.sql`

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

## indexing/shared/010_documents_list.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/010_documents_list.sql`

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

## indexing/shared/011_drafts_delete.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/011_drafts_delete.sql`

### SQL種別

DELETE

### SQLの概要

現在の組織に属する指定の下書きの記録を削除する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | drafts | D |


### 引数

| 引数 | 型 |
| --- | --- |
| params | DraftsDeleteParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `int`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の下書きの記録を削除する。 */
DELETE FROM drafts
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## indexing/shared/012_drafts_list.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/012_drafts_list.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する下書きを識別子順に一覧取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | drafts | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | DraftsListParams |
| params.organization_id | str |


### 戻り値

型: `list[DraftsListRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| document_id | str |
| body_key | str |
| body_hash | str |
| placements | str |
| revision | int |
| updated_by | str |


### 条件

WHERE organization_id = %(organization_id)s

ORDER BY id

```sql
/* 現在の組織に属する下書きを識別子順に一覧取得する。 */
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

## indexing/shared/013_ocr_runs_delete.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/013_ocr_runs_delete.sql`

### SQL種別

DELETE

### SQLの概要

現在の組織に属する指定の文字認識の実行記録の記録を削除する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | ocr_runs | D |


### 引数

| 引数 | 型 |
| --- | --- |
| params | OcrRunsDeleteParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `int`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の文字認識の実行記録の記録を削除する。 */
DELETE FROM ocr_runs
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## indexing/shared/014_ocr_runs_get.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/014_ocr_runs_get.sql`

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

## indexing/shared/015_ocr_runs_list.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/015_ocr_runs_list.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する文字認識の実行記録を識別子順に一覧取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | ocr_runs | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | OcrRunsListParams |
| params.organization_id | str |


### 戻り値

型: `list[OcrRunsListRow]`

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

WHERE organization_id = %(organization_id)s

ORDER BY id

```sql
/* 現在の組織に属する文字認識の実行記録を識別子順に一覧取得する。 */
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

## indexing/shared/016_outbox_get.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/016_outbox_get.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | outbox | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | OutboxGetParams |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `list[OutboxGetRow]`

| 取得項目 | 型（NULL制約を含む） |
| --- | --- |
| id | str |
| organization_id | str |
| document_id | str |
| version_id | str &#124; None |
| kind | str |
| status | str |
| attempts | int |
| error_code | str |
| created_at | datetime |


### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を取得する。 */
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

## indexing/shared/017_outbox_update.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/017_outbox_update.sql`

### SQL種別

UPDATE

### SQLの概要

現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | outbox | U |


### 引数

| 引数 | 型 |
| --- | --- |
| params | OutboxUpdateParams |
| params.document_id | str |
| params.version_id | str &#124; None |
| params.kind | str |
| params.status | str |
| params.attempts | int |
| params.error_code | str |
| params.created_at | datetime |
| params.organization_id | str |
| params.id | str |


### 戻り値

型: `int`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s

```sql
/* 現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。 */
UPDATE outbox SET document_id = %(document_id)s, version_id = %(version_id)s, kind = %(kind)s, status = %(status)s, attempts = %(attempts)s, error_code = %(error_code)s, created_at = %(created_at)s
WHERE
  organization_id = %(organization_id)s AND id = %(id)s
```

## indexing/shared/018_versions_get.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/018_versions_get.sql`

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

## indexing/shared/019_versions_list.sql

正本: `backend/src/kotorelay/operations/indexing/shared/sql/019_versions_list.sql`

### SQL種別

SELECT

### SQLの概要

現在の組織に属する文書版を識別子順に一覧取得する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | versions | R |


### 引数

| 引数 | 型 |
| --- | --- |
| params | VersionsListParams |
| params.organization_id | str |


### 戻り値

型: `list[VersionsListRow]`

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

WHERE organization_id = %(organization_id)s

ORDER BY id

```sql
/* 現在の組織に属する文書版を識別子順に一覧取得する。 */
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

## system/authorization/007_organizations_fence.sql

正本: `backend/src/kotorelay/operations/system/authorization/sql/007_organizations_fence.sql`

### SQL種別

UPDATE

### SQLの概要

組織の改訂番号が一致する場合だけ番号を進め、認可判定と権限失効の競合を検出する。

### 利用するテーブル

| DB | テーブル | CRUD |
| --- | --- | --- |
| PostgreSQL / DSQL | organizations | U |


### 引数

| 引数 | 型 |
| --- | --- |
| params | OrganizationsFenceParams |
| params.organization_id | str |
| params.id | str |
| params.revision | int |


### 戻り値

型: `int`

### 条件

WHERE organization_id = %(organization_id)s AND id = %(id)s AND revision = %(revision)s

```sql
/* 組織の改訂番号が一致する場合だけ番号を進め、認可判定と権限失効の競合を検出する。 */
UPDATE organizations SET revision = revision + 1
WHERE
  organization_id = %(organization_id)s AND id = %(id)s AND revision = %(revision)s
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