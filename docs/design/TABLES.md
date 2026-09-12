# KotoRelay — テーブル・カラム辞書

版0.2 / 2026-09-12 / 提案設計。`design/data/model.py` から生成。実DBのas-builtではない。

**33テーブル / 387カラム / 90外部キー / 21追加検索インデックス**。全テーブルを専用スキーマ `kotorelay` に置く。

全ての `id` はランダムUUIDの主キー。`organization_id` は複合FKと全APIのWHERE条件に使用する。NULL可以外はNOT NULL。DEFAULTを省き、アプリが値を明示する。S3バケットは環境設定で固定し、DBの任意バケット名から読み込まない。

| テーブル | 役割 |
| --- | --- |
| [organizations](#organizations) | 導入組織。初期は一組織。 |
| [users](#users) | Cognitoの本人とアプリ利用者の対応。 |
| [departments](#departments) | 部署。初期の公開・管理境界。 |
| [department_memberships](#department_memberships) | 兼務を含む利用者と部署の所属・操作権限。 |
| [documents](#documents) | 版をまたぐ文書ID、所有部署、現行認可。 |
| [document_department_grants](#document_department_grants) | 文書を追加公開する部署。 |
| [document_versions](#document_versions) | 本文と画像/OCR manifestを凍結した文書版。 |
| [document_drafts](#document_drafts) | 一文書一つの作業コピー。 |
| [review_requests](#review_requests) | 版ごとに一回の審査申請と最終決定。 |
| [document_review_slots](#document_review_slots) | 一文書一件の審査待ちを担保する予約行。 |
| [image_assets](#image_assets) | アップロードされた画像原本。文書所有で不変。 |
| [image_variants](#image_variants) | 正規化画像・モデル入力画像の不変な派生版。 |
| [ocr_runs](#ocr_runs) | 画像ごとのOCR実行・訂正結果の不変スナップショット。 |
| [ocr_regions](#ocr_regions) | OCRの文字列・読み順・画像内座標。 |
| [draft_image_placements](#draft_image_placements) | 下書きMarkdownへの画像挿入箇所。 |
| [version_image_placements](#version_image_placements) | 承認対象版に固定された画像配置とOCR。 |
| [index_builds](#index_builds) | 承認版の検索索引を構築する世代と実行状態。 |
| [document_publications](#document_publications) | 最新承認版とRAGで使える索引世代の参照。 |
| [chunks](#chunks) | 検索単位のテキストと出所。 |
| [chunk_images](#chunk_images) | チャンクと画像配置の多対多関係。 |
| [chunk_ocr_regions](#chunk_ocr_regions) | チャンクに採用したOCR領域の正確な来歴。 |
| [rag_conversations](#rag_conversations) | 利用者所有の短期チャットセッション。 |
| [rag_requests](#rag_requests) | 一回のユーザー質問。利用数の基準。 |
| [rag_answers](#rag_answers) | 確定した回答と根拠manifest。 |
| [rag_evidence](#rag_evidence) | 確定回答に使ったチャンク、引用、送信画像の記録。 |
| [model_invocations](#model_invocations) | 質問に紐づく各モデル呼出し。再試行も別記録。 |
| [usage_events](#usage_events) | 二重計上を防ぐ利用イベントの正本。 |
| [department_daily_usage](#department_daily_usage) | 部署が消費したRAG・閲覧の再計算可能な日次集計。 |
| [document_daily_usage](#document_daily_usage) | 所有部署が確認する文書別の閲覧とRAG貢献。 |
| [audit_events](#audit_events) | 権限・審査・削除等の改変を制限した業務監査。 |
| [outbox_events](#outbox_events) | 業務更新と同時に確定する非同期配送予定。 |
| [idempotency_records](#idempotency_records) | 編集・申請・審査・削除APIの再送結果。 |
| [deletion_jobs](#deletion_jobs) | 論理削除後の段階的な物理削除。 |

## organizations

導入組織。初期は一組織。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `code` | `varchar(64)` | 不可 | URLや運用で用いる組織コード。 |
| `name` | `varchar(200)` | 不可 | 組織表示名。 |
| `status` | `varchar(16)` | 不可 | active / suspended。 |
| `auth_revision` | `bigint` | 不可 | 組織停止等の認可世代。1から単調増加。 |
| `report_timezone` | `varchar(64)` | 不可 | 日次集計のIANA時刻帯。初期案 Asia/Tokyo。 |
| `created_at` | `timestamptz` | 不可 | 作成時刻 UTC。 |

主キー: `id`。

一意制約: `code`。

DBチェック: `status IN ('active','suspended')` / `auth_revision > 0`。

## users

Cognitoの本人とアプリ利用者の対応。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `cognito_subject` | `varchar(128)` | 不可 | 検証済みJWTのsub。メールは主キーにしない。 |
| `display_name` | `varchar(200)` | 不可 | 画面表示用氏名。 |
| `status` | `varchar(16)` | 不可 | active / disabled。 |
| `auth_revision` | `bigint` | 不可 | アカウント状態変更時の認可世代。 |
| `created_at` | `timestamptz` | 不可 | 作成時刻。 |
| `disabled_at` | `timestamptz` | 可 | 無効化時刻。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, cognito_subject`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`

DBチェック: `status IN ('active','disabled')` / `auth_revision > 0`。

## departments

部署。初期の公開・管理境界。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `code` | `varchar(64)` | 不可 | 組織内で一意の部署コード。 |
| `name` | `varchar(200)` | 不可 | 部署名。 |
| `status` | `varchar(16)` | 不可 | active / archived。 |
| `auth_revision` | `bigint` | 不可 | 部署状態変更時の認可世代。 |
| `created_at` | `timestamptz` | 不可 | 作成時刻。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, code`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`

DBチェック: `status IN ('active','archived')` / `auth_revision > 0`。

業務制約・更新規則: 初期版はフラットな部署。親部署からの権限自動継承は行わない。廃止前に所有文書と所属を処理する。

## department_memberships

兼務を含む利用者と部署の所属・操作権限。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `department_id` | `uuid` | 不可 | 所属部署。 |
| `user_id` | `uuid` | 不可 | 利用者。 |
| `role` | `varchar(16)` | 不可 | member / leader。 |
| `can_author` | `boolean` | 不可 | 所有部署の文書の執筆権限。 |
| `can_review` | `boolean` | 不可 | 所有部署の文書の審査権限。leaderとは独立。 |
| `status` | `varchar(16)` | 不可 | active / revoked。 |
| `auth_revision` | `bigint` | 不可 | 所属・権限変更時に増分。 |
| `joined_at` | `timestamptz` | 不可 | 所属開始時刻。 |
| `revoked_at` | `timestamptz` | 可 | 失効時刻。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, department_id, user_id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, department_id)` → `departments(organization_id, id)`
- `(organization_id, user_id)` → `users(organization_id, id)`

DBチェック: `role IN ('member','leader')` / `status IN ('active','revoked')` / `auth_revision > 0`。

検索インデックス: `organization_id, user_id, status, department_id`。

業務制約・更新規則: 同部署への再所属では同じ行を再有効化して世代を増やし、前歴は監査に残す。can_author/can_reviewは部署所有の全文書に適用する初期案。個別担当者制限は後続拡張。

## documents

版をまたぐ文書ID、所有部署、現行認可。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `owner_department_id` | `uuid` | 不可 | 管理と削除を行える所有部署。共有先とは別。 |
| `created_by` | `uuid` | 不可 | 初回作成者。 |
| `visibility` | `varchar(16)` | 不可 | department / selected / organization。 |
| `search_scope_token` | `uuid` | 不可 | 文書ACL変更ごとに更新する検索フィルター識別子。秘密鍵ではない。 |
| `status` | `varchar(16)` | 不可 | active / withdrawn / deleted。 |
| `next_version_no` | `bigint` | 不可 | 次の版確定で払い出す番号。CAS更新。 |
| `auth_revision` | `bigint` | 不可 | 公開範囲・削除・公開停止・所属境界変更時に増分。 |
| `row_revision` | `bigint` | 不可 | 書込み競合検知用の更新番号。 |
| `created_at` | `timestamptz` | 不可 | 作成時刻。 |
| `updated_at` | `timestamptz` | 不可 | メタデータ更新時刻。 |
| `deleted_at` | `timestamptz` | 可 | 論理削除時刻。 |
| `deleted_by` | `uuid` | 可 | 削除実行者。論理削除時に必須。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, search_scope_token`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, owner_department_id)` → `departments(organization_id, id)`
- `(organization_id, created_by)` → `users(organization_id, id)`
- `(organization_id, deleted_by)` → `users(organization_id, id)`

DBチェック: `visibility IN ('department','selected','organization')` / `status IN ('active','withdrawn','deleted')` / `next_version_no > 0 AND auth_revision > 0 AND row_revision > 0` / `(status = 'deleted' AND deleted_at IS NOT NULL AND deleted_by IS NOT NULL) OR (status <> 'deleted' AND deleted_at IS NULL AND deleted_by IS NULL)`。

検索インデックス: `organization_id, owner_department_id, status, updated_at, id`。

業務制約・更新規則: 未承認タイトルを共通一覧へ漏らさないため、タイトルは下書き・版に保持。所有部署の変更は初期UI対象外。必要なら専用移管フローで認可世代と統計の帰属を扱う。

## document_department_grants

文書を追加公開する部署。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `document_id` | `uuid` | 不可 | 共有される文書。 |
| `department_id` | `uuid` | 不可 | 追加の閲覧許可先。 |
| `created_by` | `uuid` | 不可 | 共有設定者。 |
| `created_at` | `timestamptz` | 不可 | 設定時刻。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, document_id, department_id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, document_id)` → `documents(organization_id, id)`
- `(organization_id, department_id)` → `departments(organization_id, id)`
- `(organization_id, created_by)` → `users(organization_id, id)`

検索インデックス: `organization_id, department_id, document_id`。

業務制約・更新規則: visibility=selectedのときに使用するread許可。編集・審査・削除は付与しない。所有部署の読取りは文書の基本規則で判定する。追加・削除とdocuments.auth_revision増分を同一トランザクションで確定。

## document_versions

本文と画像/OCR manifestを凍結した文書版。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `document_id` | `uuid` | 不可 | 論理文書。 |
| `version_no` | `bigint` | 不可 | 文書内で単調増加する版番号。 |
| `title` | `varchar(500)` | 不可 | この版のタイトル。 |
| `body_object_key` | `text` | 不可 | 非公開S3上のMarkdownキー。 |
| `body_s3_version_id` | `text` | 不可 | S3の厳密なオブジェクト版。 |
| `body_sha256` | `varchar(64)` | 不可 | Markdown UTF-8バイト列のSHA-256。 |
| `manifest_object_key` | `text` | 不可 | 画像配置・画像hash・OCR runを含むmanifestのS3キー。 |
| `manifest_s3_version_id` | `text` | 不可 | manifestのS3版。 |
| `manifest_sha256` | `varchar(64)` | 不可 | 承認対象全体の正規化manifest hash。 |
| `freeze_status` | `varchar(16)` | 不可 | staging / sealed。sealed後に申請可能。 |
| `image_count` | `integer` | 不可 | 画像配置の件数。同一画像の複数配置も数える。 |
| `created_by` | `uuid` | 不可 | 版確定者。 |
| `created_at` | `timestamptz` | 不可 | 版生成開始時刻。 |
| `sealed_at` | `timestamptz` | 可 | 全配置の保存・検証完了時刻。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, document_id, version_no` / `organization_id, document_id, id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, document_id)` → `documents(organization_id, id)`
- `(organization_id, created_by)` → `users(organization_id, id)`

DBチェック: `version_no > 0 AND image_count >= 0` / `freeze_status IN ('staging','sealed')` / `(freeze_status = 'sealed') = (sealed_at IS NOT NULL)`。

業務制約・更新規則: sealed版の本文・配置・OCR参照をUPDATEしない。大量の画像配置はstagingに分割登録し、manifest検証後の短いトランザクションでsealedにする。stagingは申請・閲覧・索引対象外。

## document_drafts

一文書一つの作業コピー。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `document_id` | `uuid` | 不可 | 編集中の文書。 |
| `base_version_id` | `uuid` | 可 | 編集開始の元版。新規時NULL。 |
| `title` | `varchar(500)` | 不可 | 作業中タイトル。 |
| `body_object_key` | `text` | 不可 | 保存済みMarkdownのS3キー。 |
| `body_s3_version_id` | `text` | 不可 | 保存済みオブジェクト版。 |
| `body_sha256` | `varchar(64)` | 不可 | 保存済み本文hash。 |
| `row_revision` | `bigint` | 不可 | 保存時If-Matchで照合する版番号。 |
| `updated_by` | `uuid` | 不可 | 最終保存者。 |
| `updated_at` | `timestamptz` | 不可 | 最終保存時刻。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, document_id` / `organization_id, document_id, id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, document_id)` → `documents(organization_id, id)`
- `(organization_id, document_id, base_version_id)` → `document_versions(organization_id, document_id, id)`
- `(organization_id, updated_by)` → `users(organization_id, id)`

DBチェック: `row_revision > 0`。

業務制約・更新規則: 編集中の未保存文字はブラウザ側。本文と画像配置変更は同じ下書きrow_revisionでCASする。審査待ち版とは別に編集できる。

## review_requests

版ごとに一回の審査申請と最終決定。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `document_id` | `uuid` | 不可 | 対象文書。 |
| `version_id` | `uuid` | 不可 | sealed版。 |
| `requested_by` | `uuid` | 不可 | 申請者。 |
| `requested_at` | `timestamptz` | 不可 | 申請時刻。 |
| `manifest_sha256` | `varchar(64)` | 不可 | 審査で確認した承認対象hash。 |
| `status` | `varchar(16)` | 不可 | pending / approved / rejected / withdrawn。 |
| `decided_by` | `uuid` | 可 | 承認・却下・取下げ実行者。 |
| `decided_at` | `timestamptz` | 可 | 決定時刻。 |
| `decision_reason` | `text` | 可 | 却下時に必須。機密扱い。 |
| `policy_version` | `varchar(64)` | 不可 | 自己承認や審査段階の運用方針版。 |
| `row_revision` | `bigint` | 不可 | 競合検知。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, version_id` / `organization_id, document_id, id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, document_id, version_id)` → `document_versions(organization_id, document_id, id)`
- `(organization_id, requested_by)` → `users(organization_id, id)`
- `(organization_id, decided_by)` → `users(organization_id, id)`

DBチェック: `status IN ('pending','approved','rejected','withdrawn')` / `row_revision > 0` / `(status = 'pending' AND decided_by IS NULL AND decided_at IS NULL) OR (status <> 'pending' AND decided_by IS NOT NULL AND decided_at IS NOT NULL)` / `status <> 'rejected' OR (decision_reason IS NOT NULL AND length(trim(decision_reason)) > 0)`。

検索インデックス: `organization_id, status, requested_at, id`。

業務制約・更新規則: pending以外を再決定しない。修正は新しい文書版と申請。申請・決定・取下げの時系列はaudit_eventsにも同一トランザクションで追記。

## document_review_slots

一文書一件の審査待ちを担保する予約行。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `document_id` | `uuid` | 不可 | 予約対象文書。 |
| `review_request_id` | `uuid` | 不可 | 現在pendingの申請。 |
| `created_at` | `timestamptz` | 不可 | 申請開始時刻。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, document_id` / `organization_id, review_request_id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, document_id, review_request_id)` → `review_requests(organization_id, document_id, id)`

業務制約・更新規則: pending化と同時INSERT、終端決定と同時DELETE。UNIQUE競合で二重申請を拒否。申請状態との一致は業務トランザクションと照合で検証。

## image_assets

アップロードされた画像原本。文書所有で不変。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `document_id` | `uuid` | 不可 | 親文書。別文書への無断参照を禁止。 |
| `original_object_key` | `text` | 不可 | 隔離領域S3の原本キー。 |
| `original_s3_version_id` | `text` | 不可 | 原本S3版。 |
| `original_sha256` | `varchar(64)` | 不可 | 原本バイナリhash。 |
| `original_filename` | `varchar(500)` | 不可 | 元ファイル名。表示時エスケープ。 |
| `media_type` | `varchar(64)` | 不可 | 検査後の実際のMIME。 |
| `byte_size` | `bigint` | 不可 | 原本サイズ。 |
| `status` | `varchar(16)` | 不可 | quarantined / ready / rejected。 |
| `uploaded_by` | `uuid` | 不可 | アップロード者。 |
| `created_at` | `timestamptz` | 不可 | 受信時刻。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, document_id, id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, document_id)` → `documents(organization_id, id)`
- `(organization_id, uploaded_by)` → `users(organization_id, id)`

DBチェック: `byte_size > 0` / `status IN ('quarantined','ready','rejected')`。

検索インデックス: `organization_id, document_id, status`。

業務制約・更新規則: 同じ画像の再利用は文書内に限定。原本は上書きせず、新しいファイルは新ID。検疫とデコード検証を通るまではOCR・通常表示しない。

## image_variants

正規化画像・モデル入力画像の不変な派生版。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `document_id` | `uuid` | 不可 | 親文書。 |
| `asset_id` | `uuid` | 不可 | 原本画像。 |
| `variant_kind` | `varchar(16)` | 不可 | canonical / model。 |
| `object_key` | `text` | 不可 | 非公開S3の実体キー。 |
| `s3_version_id` | `text` | 不可 | S3の厳密な版。 |
| `sha256` | `varchar(64)` | 不可 | 派生画像hash。 |
| `media_type` | `varchar(32)` | 不可 | image/png / image/jpeg。 |
| `byte_size` | `bigint` | 不可 | 派生画像バイト数。 |
| `width_px` | `integer` | 不可 | EXIF回転適用後の幅。 |
| `height_px` | `integer` | 不可 | EXIF回転適用後の高さ。 |
| `transform_json` | `jsonb` | 不可 | 原本→この画像の回転・拡縮・crop・変換行列。 |
| `processor_version` | `varchar(128)` | 不可 | 画像変換設定・ライブラリ・コード版。 |
| `created_at` | `timestamptz` | 不可 | 生成時刻。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, document_id, asset_id, id` / `organization_id, asset_id, variant_kind, processor_version`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, document_id, asset_id)` → `image_assets(organization_id, document_id, id)`

DBチェック: `variant_kind IN ('canonical','model')` / `media_type IN ('image/png','image/jpeg')` / `byte_size > 0 AND width_px > 0 AND height_px > 0`。

業務制約・更新規則: OCR座標はcanonical基準。model版で縮小してもcanonicalとの変換を追える。読取不能になる縮小を禁止。base64は保存しない。

## ocr_runs

画像ごとのOCR実行・訂正結果の不変スナップショット。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `document_id` | `uuid` | 不可 | 親文書。 |
| `asset_id` | `uuid` | 不可 | 対象画像。 |
| `variant_id` | `uuid` | 不可 | OCRしたcanonical画像。 |
| `engine` | `varchar(64)` | 不可 | 例 paddleocr / human_correction。 |
| `engine_version` | `varchar(128)` | 不可 | ライブラリ・モデル重み識別子。 |
| `config_sha256` | `varchar(64)` | 不可 | 言語・閾値・モデルchecksumを含む設定hash。 |
| `source_run_id` | `uuid` | 可 | 再OCR・訂正の元run。 |
| `status` | `varchar(16)` | 不可 | queued / running / succeeded / no_text / failed。 |
| `region_count` | `integer` | 不可 | 認識領域数。 |
| `raw_result_key` | `text` | 可 | 全文JSONのS3キー。入力画像は含めない。 |
| `raw_result_s3_version_id` | `text` | 可 | 結果JSONのS3版。 |
| `result_sha256` | `varchar(64)` | 可 | 完了したOCR結果全体のhash。 |
| `review_status` | `varchar(16)` | 不可 | unchecked / accepted / needs_fix。 |
| `reviewed_by` | `uuid` | 可 | OCR結果を確認した編集者。 |
| `reviewed_at` | `timestamptz` | 可 | OCR確認時刻。 |
| `error_code` | `varchar(64)` | 可 | 機密文字を含めない失敗コード。 |
| `started_at` | `timestamptz` | 可 | 実行開始。 |
| `finished_at` | `timestamptz` | 可 | 実行完了。 |
| `created_at` | `timestamptz` | 不可 | 受付時刻。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, document_id, asset_id, id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, document_id, asset_id, variant_id)` → `image_variants(organization_id, document_id, asset_id, id)`
- `(organization_id, document_id, asset_id, source_run_id)` → `ocr_runs(organization_id, document_id, asset_id, id)`
- `(organization_id, reviewed_by)` → `users(organization_id, id)`

DBチェック: `status IN ('queued','running','succeeded','no_text','failed')` / `review_status IN ('unchecked','accepted','needs_fix')` / `region_count >= 0` / `status NOT IN ('succeeded','no_text') OR (result_sha256 IS NOT NULL AND finished_at IS NOT NULL)` / `review_status <> 'accepted' OR (reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL AND status IN ('succeeded','no_text'))`。

検索インデックス: `organization_id, asset_id, created_at`。

業務制約・更新規則: 完了後の文字・座標は上書きしない。人の訂正も新runとして旧runを参照。no_textは文字のない図の正常結果で、failedとは区別。

## ocr_regions

OCRの文字列・読み順・画像内座標。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `document_id` | `uuid` | 不可 | 親文書。 |
| `asset_id` | `uuid` | 不可 | 画像。 |
| `ocr_run_id` | `uuid` | 不可 | 結果スナップショット。 |
| `region_no` | `integer` | 不可 | run内で一意の領域番号。 |
| `reading_order` | `integer` | 不可 | 論理的な読み順。0から。 |
| `text_content` | `text` | 不可 | 領域の文字起こし。上限をアプリで検証。 |
| `x` | `numeric(8,6)` | 不可 | 左端。canonical幅で正規化した0〜1。 |
| `y` | `numeric(8,6)` | 不可 | 上端。canonical高さで正規化した0〜1。 |
| `width` | `numeric(8,6)` | 不可 | 正規化した矩形幅。 |
| `height` | `numeric(8,6)` | 不可 | 正規化した矩形高さ。 |
| `polygon_json` | `jsonb` | 不可 | 左上原点、時計回りの正規化頂点 [[x,y],...]。 |
| `confidence` | `numeric(8,6)` | 可 | OCR信頼度を0〜1に正規化。人による訂正はNULL可。 |
| `region_kind` | `varchar(16)` | 不可 | line / word / paragraph。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, ocr_run_id, region_no` / `organization_id, document_id, asset_id, ocr_run_id, id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, document_id, asset_id, ocr_run_id)` → `ocr_runs(organization_id, document_id, asset_id, id)`

DBチェック: `region_no >= 0 AND reading_order >= 0` / `x >= 0 AND y >= 0 AND width > 0 AND height > 0 AND x + width <= 1 AND y + height <= 1` / `confidence IS NULL OR (confidence >= 0 AND confidence <= 1)` / `region_kind IN ('line','word','paragraph')`。

検索インデックス: `organization_id, ocr_run_id, reading_order`。

業務制約・更新規則: polygonの頂点数・値域・自己交差・bboxとの整合はアプリ検証。保存文字列と座標を審査画面で画像に重ねて確認。

## draft_image_placements

下書きMarkdownへの画像挿入箇所。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `document_id` | `uuid` | 不可 | 親文書。 |
| `draft_id` | `uuid` | 不可 | 編集中の下書き。 |
| `asset_id` | `uuid` | 不可 | 添付画像。 |
| `ocr_run_id` | `uuid` | 可 | 編集中に採用するOCR結果。未完了時NULL。 |
| `anchor_id` | `uuid` | 不可 | エディターASTの安定した画像ノードID。 |
| `ordinal` | `integer` | 不可 | 文書内の画像出現順。 |
| `source_start_byte` | `integer` | 不可 | 保存済みMarkdownの画像記法開始UTF-8バイト位置。 |
| `source_end_byte` | `integer` | 不可 | 終了位置。半開区間。 |
| `alt_text` | `text` | 不可 | 代替テキスト。 |
| `caption` | `text` | 可 | 図の説明。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, draft_id, anchor_id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, document_id, draft_id)` → `document_drafts(organization_id, document_id, id)`
- `(organization_id, document_id, asset_id)` → `image_assets(organization_id, document_id, id)`
- `(organization_id, document_id, asset_id, ocr_run_id)` → `ocr_runs(organization_id, document_id, asset_id, id)`

DBチェック: `ordinal >= 0 AND source_start_byte >= 0 AND source_end_byte > source_start_byte`。

業務制約・更新規則: 配置の挿入・移動・削除は下書きCASと同一トランザクション。offsetだけに頼らずanchor_idで編集時の位置を追う。

## version_image_placements

承認対象版に固定された画像配置とOCR。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `document_id` | `uuid` | 不可 | 親文書。 |
| `version_id` | `uuid` | 不可 | 変更不能な文書版。 |
| `asset_id` | `uuid` | 不可 | 添付原本。 |
| `ocr_run_id` | `uuid` | 不可 | 審査対象に含める完了・確認済みOCR。 |
| `anchor_id` | `uuid` | 不可 | この版に凍結したASTノードID。 |
| `ordinal` | `integer` | 不可 | 画像出現順。 |
| `source_start_byte` | `integer` | 不可 | この版本文のUTF-8バイト開始位置。 |
| `source_end_byte` | `integer` | 不可 | 半開区間の終了位置。 |
| `heading_path_json` | `jsonb` | 不可 | 画像が属する見出し階層。 |
| `alt_text` | `text` | 不可 | この版の代替テキスト。 |
| `caption` | `text` | 可 | この版の説明。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, version_id, anchor_id` / `organization_id, document_id, version_id, id` / `organization_id, document_id, version_id, id, asset_id, ocr_run_id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, document_id, version_id)` → `document_versions(organization_id, document_id, id)`
- `(organization_id, document_id, asset_id, ocr_run_id)` → `ocr_runs(organization_id, document_id, asset_id, id)`

DBチェック: `ordinal >= 0 AND source_start_byte >= 0 AND source_end_byte > source_start_byte`。

業務制約・更新規則: 同じassetの二箇所への添付は別id/anchor。sealed後は削除・差替え不可。画像・OCRの訂正には新しい文書版の承認が必要。

## index_builds

承認版の検索索引を構築する世代と実行状態。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `document_id` | `uuid` | 不可 | 親文書。 |
| `version_id` | `uuid` | 不可 | 承認済み対象版。 |
| `generation_no` | `bigint` | 不可 | 版内の索引構築世代。 |
| `status` | `varchar(16)` | 不可 | queued / processing / verifying / ready / failed / obsolete。 |
| `manifest_sha256` | `varchar(64)` | 不可 | 入力の承認対象hash。 |
| `search_scope_token` | `uuid` | 不可 | 構築時の文書検索scope世代。過去値保持のためこの値へのFKは張らない。 |
| `pipeline_version` | `varchar(128)` | 不可 | パーサ・chunker・OCR結合の設定版。 |
| `embedding_model_id` | `varchar(200)` | 不可 | 埋め込みモデル識別子。 |
| `kb_job_id` | `varchar(200)` | 可 | KB取り込みジョブID。 |
| `expected_chunk_count` | `integer` | 不可 | 作成予定チャンク数。 |
| `verified_chunk_count` | `integer` | 不可 | 出所・件数・取得を検証済みの件数。 |
| `error_code` | `varchar(64)` | 可 | 安全な失敗分類。 |
| `created_at` | `timestamptz` | 不可 | 起動時刻。 |
| `ready_at` | `timestamptz` | 可 | 反映検証完了時刻。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, version_id, generation_no` / `organization_id, document_id, version_id, id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, document_id, version_id)` → `document_versions(organization_id, document_id, id)`

DBチェック: `generation_no > 0 AND expected_chunk_count >= 0 AND verified_chunk_count >= 0` / `status IN ('queued','processing','verifying','ready','failed','obsolete')` / `status <> 'ready' OR (ready_at IS NOT NULL AND expected_chunk_count > 0 AND expected_chunk_count = verified_chunk_count)`。

検索インデックス: `organization_id, status, created_at`。

業務制約・更新規則: KBのCOMPLETEだけでreadyにしない。索引自体はS3 Vectors。DSQLは検索許可と来歴の正本でありベクトルDBとして用いない。

## document_publications

最新承認版とRAGで使える索引世代の参照。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `document_id` | `uuid` | 不可 | 一文書一行。 |
| `latest_approved_version_id` | `uuid` | 不可 | 版番号が最大の承認済み版。 |
| `active_index_build_id` | `uuid` | 可 | 利用可能な同じ版の索引。未反映時NULL。 |
| `row_revision` | `bigint` | 不可 | 承認・索引切替のCAS世代。 |
| `updated_at` | `timestamptz` | 不可 | 公開制御更新時刻。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, document_id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, document_id, latest_approved_version_id)` → `document_versions(organization_id, document_id, id)`
- `(organization_id, document_id, latest_approved_version_id, active_index_build_id)` → `index_builds(organization_id, document_id, version_id, id)`

DBチェック: `row_revision > 0`。

業務制約・更新規則: 承認時にreview_requestsと同時更新。新版が承認されたらactive_index_build_idをNULLにし、旧版へのfallbackを防ぐ。公開停止・削除はdocuments側も必ず判定する。

## chunks

検索単位のテキストと出所。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `document_id` | `uuid` | 不可 | 親文書。 |
| `version_id` | `uuid` | 不可 | 承認済み版。 |
| `index_build_id` | `uuid` | 不可 | 構築世代。 |
| `chunk_no` | `integer` | 不可 | build内のチャンク順。 |
| `text_object_key` | `text` | 不可 | MarkdownとOCR文字を結合したS3検索入力。 |
| `text_s3_version_id` | `text` | 不可 | 検索入力S3版。 |
| `text_sha256` | `varchar(64)` | 不可 | 結合テキストhash。 |
| `source_start_byte` | `integer` | 不可 | 原Markdownの対応範囲先頭。 |
| `source_end_byte` | `integer` | 不可 | 原Markdown範囲の半開区間末尾。 |
| `heading_path_json` | `jsonb` | 不可 | 見出し階層。 |
| `token_count` | `integer` | 不可 | 使用tokenizerによるトークン数。 |
| `vector_record_key` | `varchar(200)` | 不可 | 索引側の識別子。必須metadata chunk_idと対応。 |
| `created_at` | `timestamptz` | 不可 | 生成時刻。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, index_build_id, chunk_no` / `organization_id, document_id, version_id, id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, document_id, version_id, index_build_id)` → `index_builds(organization_id, document_id, version_id, id)`

DBチェック: `chunk_no >= 0 AND token_count >= 0` / `source_start_byte >= 0 AND source_end_byte >= source_start_byte`。

業務制約・更新規則: 一チャンク一入力オブジェクト、KBの追加chunkingなしを第一候補。OCRだけの補助chunkは元画像記法の位置を保持。UTF-8バイトoffsetは本文にのみ適用し、OCR位置は領域リンクで表す。

## chunk_images

チャンクと画像配置の多対多関係。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `document_id` | `uuid` | 不可 | 親文書。 |
| `version_id` | `uuid` | 不可 | 親文書版。 |
| `chunk_id` | `uuid` | 不可 | 画像を含むチャンク。 |
| `placement_id` | `uuid` | 不可 | 同版の画像出現箇所。 |
| `asset_id` | `uuid` | 不可 | 配置が参照する画像。 |
| `ocr_run_id` | `uuid` | 不可 | 配置が参照するOCR。 |
| `link_reason` | `varchar(24)` | 不可 | source_overlap / ocr_evidence / contextual。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, chunk_id, placement_id` / `organization_id, document_id, chunk_id, placement_id, asset_id, ocr_run_id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, document_id, version_id, chunk_id)` → `chunks(organization_id, document_id, version_id, id)`
- `(organization_id, document_id, version_id, placement_id, asset_id, ocr_run_id)` → `version_image_placements(organization_id, document_id, version_id, id, asset_id, ocr_run_id)`

DBチェック: `link_reason IN ('source_overlap','ocr_evidence','contextual')`。

業務制約・更新規則: 画像挿入箇所を含むchunk、OCR文字の分割chunk、図への直接参照chunkに明示的に結び付ける。採用chunkの全リンク画像をモデルへ送る。

## chunk_ocr_regions

チャンクに採用したOCR領域の正確な来歴。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `document_id` | `uuid` | 不可 | 親文書。 |
| `chunk_id` | `uuid` | 不可 | 検索チャンク。 |
| `placement_id` | `uuid` | 不可 | 文書内の画像配置。 |
| `asset_id` | `uuid` | 不可 | 画像。 |
| `ocr_run_id` | `uuid` | 不可 | OCR結果。 |
| `region_id` | `uuid` | 不可 | その結果中の文字・座標領域。 |
| `text_start_char` | `integer` | 不可 | 領域文字列で採用したUnicode code point先頭。 |
| `text_end_char` | `integer` | 不可 | 採用した文字の半開区間末尾。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, chunk_id, placement_id, region_id, text_start_char`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, document_id, chunk_id, placement_id, asset_id, ocr_run_id)` → `chunk_images(organization_id, document_id, chunk_id, placement_id, asset_id, ocr_run_id)`
- `(organization_id, document_id, asset_id, ocr_run_id, region_id)` → `ocr_regions(organization_id, document_id, asset_id, ocr_run_id, id)`

DBチェック: `text_start_char >= 0 AND text_end_char > text_start_char`。

業務制約・更新規則: OCRの一領域が長く二分されても元regionと文字範囲を復元できる。DB文字長と上限の照合はアプリ。JS UTF-16 offsetを無変換で格納しない。

## rag_conversations

利用者所有の短期チャットセッション。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `owner_user_id` | `uuid` | 不可 | 会話所有者。 |
| `acting_department_id` | `uuid` | 不可 | この会話の利用部署。開始時に現在所属を検証。 |
| `created_at` | `timestamptz` | 不可 | 開始時刻。 |
| `expires_at` | `timestamptz` | 不可 | 会話本文の保持期限。 |
| `status` | `varchar(16)` | 不可 | active / deleted / expired。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, id, owner_user_id, acting_department_id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, owner_user_id)` → `users(organization_id, id)`
- `(organization_id, acting_department_id)` → `departments(organization_id, id)`

DBチェック: `status IN ('active','deleted','expired')` / `expires_at > created_at`。

検索インデックス: `organization_id, owner_user_id, created_at`。

業務制約・更新規則: 利用部署の切替は新会話。追質問・取得ごとに所有者と現在所属を再認可。他人の会話本文をリーダーへ開示しない。

## rag_requests

一回のユーザー質問。利用数の基準。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `conversation_id` | `uuid` | 不可 | 会話。 |
| `user_id` | `uuid` | 不可 | 質問者。 |
| `acting_department_id` | `uuid` | 不可 | 消費側部署の履歴スナップショット。 |
| `idempotency_key` | `varchar(128)` | 不可 | 同じ質問再送を識別するキー。 |
| `question_object_key` | `text` | 不可 | 暗号化・短期保持する質問S3キー。 |
| `question_s3_version_id` | `text` | 不可 | 質問オブジェクト版。 |
| `question_sha256` | `varchar(64)` | 不可 | 同一キーで異なる質問を拒否するhash。 |
| `status` | `varchar(16)` | 不可 | accepted / running / answered / abstained / failed / cancelled。 |
| `policy_version` | `varchar(128)` | 不可 | 認可・prompt方針版。 |
| `retrieval_config_version` | `varchar(128)` | 不可 | 検索設定版。 |
| `auth_snapshot_json` | `jsonb` | 不可 | 認可時の組織・ユーザー・所属のIDと世代。権限の現行正本ではない。 |
| `accepted_at` | `timestamptz` | 不可 | 認証・上限確認後に受付が確定した時刻。 |
| `completed_at` | `timestamptz` | 可 | 終端状態確定時刻。 |
| `error_code` | `varchar(64)` | 可 | 本文を含めない失敗分類。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, user_id, idempotency_key`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, conversation_id, user_id, acting_department_id)` → `rag_conversations(organization_id, id, owner_user_id, acting_department_id)`

DBチェック: `status IN ('accepted','running','answered','abstained','failed','cancelled')`。

検索インデックス: `organization_id, acting_department_id, accepted_at, id` / `organization_id, conversation_id, accepted_at`。

業務制約・更新規則: 利用数はacceptedの質問IDを一件とする。モデル再試行で新しい質問行を作らない。モデルに送る直前はsnapshotを信用せず最新認可を取り直す。

## rag_answers

確定した回答と根拠manifest。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `request_id` | `uuid` | 不可 | 対応質問。一質問につき確定結果一件。 |
| `outcome` | `varchar(16)` | 不可 | answered / abstained。 |
| `body_object_key` | `text` | 不可 | 暗号化した回答S3キー。 |
| `body_s3_version_id` | `text` | 不可 | 回答S3版。 |
| `body_sha256` | `varchar(64)` | 不可 | 回答hash。 |
| `evidence_manifest_sha256` | `varchar(64)` | 不可 | 引用版・chunk・画像の集合hash。 |
| `auth_fence_json` | `jsonb` | 不可 | 確定時に確認した認可・公開制御世代。 |
| `finalized_at` | `timestamptz` | 不可 | 回答の確定点。 |
| `expires_at` | `timestamptz` | 不可 | 本文保持期限。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, request_id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, request_id)` → `rag_requests(organization_id, id)`

DBチェック: `outcome IN ('answered','abstained')` / `expires_at > finalized_at`。

業務制約・更新規則: 履歴・再配信ごとにevidenceの現在ACLと公開版を照合。無効な根拠を含む回答全体を隠す。送信済み情報を回収する保証はしない。

## rag_evidence

確定回答に使ったチャンク、引用、送信画像の記録。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `answer_id` | `uuid` | 不可 | 回答。 |
| `document_id` | `uuid` | 不可 | 引用文書。 |
| `version_id` | `uuid` | 不可 | 実際に使った版。 |
| `chunk_id` | `uuid` | 不可 | 実際に使ったチャンク。 |
| `citation_no` | `integer` | 不可 | サーバー発行の引用番号。 |
| `rank_no` | `integer` | 不可 | モデル入力内の根拠順。 |
| `owner_department_id_snapshot` | `uuid` | 不可 | 利用時の文書所有部署。貢献集計用。 |
| `image_inputs_json` | `jsonb` | 不可 | 入力画像のasset/variant/placement ID・hash・形式・サイズ・順序。base64や本文を含めない。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, answer_id, chunk_id` / `organization_id, answer_id, citation_no`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, answer_id)` → `rag_answers(organization_id, id)`
- `(organization_id, document_id, version_id, chunk_id)` → `chunks(organization_id, document_id, version_id, id)`
- `(organization_id, owner_department_id_snapshot)` → `departments(organization_id, id)`

DBチェック: `citation_no > 0 AND rank_no > 0`。

検索インデックス: `organization_id, document_id, answer_id`。

業務制約・更新規則: image_inputs_jsonは監査用の不変manifestであり検索用マスターではない。image_variants/chunk_imagesとの完全一致をアプリで検証し、未登録の画像を生成へ送らない。出典URLはIDからサーバーが生成する。

## model_invocations

質問に紐づく各モデル呼出し。再試行も別記録。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `request_id` | `uuid` | 不可 | ユーザー質問。 |
| `phase` | `varchar(16)` | 不可 | rewrite / rerank / generate。 |
| `attempt_no` | `integer` | 不可 | 工程内の試行番号。 |
| `model_id` | `varchar(200)` | 不可 | 実際のモデルまたはinference profile。 |
| `input_tokens` | `bigint` | 可 | 実測入力トークン。 |
| `output_tokens` | `bigint` | 可 | 実測出力トークン。 |
| `image_count` | `integer` | 不可 | 実際のユニーク入力画像数。 |
| `image_bytes` | `bigint` | 不可 | base64変換前の合計バイト数。 |
| `input_manifest_sha256` | `varchar(64)` | 不可 | 呼出し全入力の追跡用hash。本文は記録しない。 |
| `input_manifest_object_key` | `text` | 不可 | 暗号化監査S3の入力ID/hash対応manifestキー。 |
| `input_manifest_s3_version_id` | `text` | 不可 | 入力manifestのS3版。 |
| `status` | `varchar(16)` | 不可 | started / succeeded / failed。 |
| `started_at` | `timestamptz` | 不可 | モデル送信直前。 |
| `finished_at` | `timestamptz` | 可 | 完了時刻。 |
| `provider_request_id` | `varchar(200)` | 可 | Bedrockの要求ID。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, request_id, phase, attempt_no`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, request_id)` → `rag_requests(organization_id, id)`

DBチェック: `phase IN ('rewrite','rerank','generate')` / `status IN ('started','succeeded','failed')` / `attempt_no > 0 AND image_count >= 0 AND image_bytes >= 0` / `input_tokens IS NULL OR input_tokens >= 0` / `output_tokens IS NULL OR output_tokens >= 0`。

業務制約・更新規則: 入力manifestの追跡先は暗号化S3の許可済み監査領域。本文・base64を通常ログへ残さない。RAG利用数とモデル呼出し数を区別する。

## usage_events

二重計上を防ぐ利用イベントの正本。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `event_kind` | `varchar(24)` | 不可 | rag_accepted / rag_answered / rag_abstained / rag_failed / rag_cancelled / document_view。 |
| `dedup_key` | `varchar(200)` | 不可 | イベント種別と質問IDまたはview IDから作る一意キー。 |
| `actor_user_id` | `uuid` | 不可 | 利用者。リーダー向け集計APIへ個人列を返さない。 |
| `acting_department_id` | `uuid` | 不可 | イベント時の消費部署。 |
| `document_id` | `uuid` | 可 | document_viewの文書。 |
| `version_id` | `uuid` | 可 | document_viewで実際に表示した承認版。 |
| `owner_department_id_snapshot` | `uuid` | 可 | 表示時の文書所有部署。 |
| `rag_request_id` | `uuid` | 可 | rag系イベントの質問。 |
| `occurred_at` | `timestamptz` | 不可 | サーバー確定時刻。 |
| `ingested_at` | `timestamptz` | 不可 | DBへの記録時刻。 |
| `expires_at` | `timestamptz` | 不可 | イベント詳細の保持期限。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, dedup_key`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, actor_user_id)` → `users(organization_id, id)`
- `(organization_id, acting_department_id)` → `departments(organization_id, id)`
- `(organization_id, document_id, version_id)` → `document_versions(organization_id, document_id, id)`
- `(organization_id, owner_department_id_snapshot)` → `departments(organization_id, id)`
- `(organization_id, rag_request_id)` → `rag_requests(organization_id, id)`

DBチェック: `event_kind IN ('rag_accepted','rag_answered','rag_abstained','rag_failed','rag_cancelled','document_view')` / `(event_kind = 'document_view' AND document_id IS NOT NULL AND version_id IS NOT NULL AND owner_department_id_snapshot IS NOT NULL AND rag_request_id IS NULL) OR (event_kind <> 'document_view' AND rag_request_id IS NOT NULL AND document_id IS NULL AND version_id IS NULL AND owner_department_id_snapshot IS NULL)`。

検索インデックス: `organization_id, acting_department_id, occurred_at, id` / `organization_id, document_id, occurred_at, id` / `organization_id, ingested_at, id`。

業務制約・更新規則: 表示確認は認可済み本文取得に結び付くサーバー発行view IDのackで記録。通信再送は同じdedup_key。一度の表示で画像取得・preview・RAG参照は閲覧として数えない。

## department_daily_usage

部署が消費したRAG・閲覧の再計算可能な日次集計。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `department_id` | `uuid` | 不可 | 利用部署。 |
| `usage_date` | `date` | 不可 | 固定したreport_timezoneの日付。 |
| `metric` | `varchar(32)` | 不可 | rag_accepted / rag_answered / rag_abstained / rag_failed / rag_cancelled / document_views / active_users。 |
| `metric_value` | `bigint` | 不可 | 確定件数または日次のユニーク利用者数。 |
| `aggregation_version` | `varchar(64)` | 不可 | 集計式版。 |
| `source_watermark` | `timestamptz` | 不可 | この取込時刻まで再計算済み。 |
| `computed_at` | `timestamptz` | 不可 | 集計更新時刻。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, department_id, usage_date, metric`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, department_id)` → `departments(organization_id, id)`

DBチェック: `metric_value >= 0` / `metric IN ('rag_accepted','rag_answered','rag_abstained','rag_failed','rag_cancelled','document_views','active_users')`。

業務制約・更新規則: raw eventsから窓単位に再計算して上書き。毎要求の同一行加算をしない。active_usersは日次値で、月次ユニーク数は日次を足さず原イベントから再算出。

## document_daily_usage

所有部署が確認する文書別の閲覧とRAG貢献。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `document_id` | `uuid` | 不可 | 対象文書。 |
| `owner_department_id_snapshot` | `uuid` | 不可 | 利用時点の所有部署。 |
| `usage_date` | `date` | 不可 | 集計日。 |
| `metric` | `varchar(32)` | 不可 | document_views / cited_answers。 |
| `metric_value` | `bigint` | 不可 | 閲覧件数、または当該文書を根拠に使った一意な確定回答数。 |
| `aggregation_version` | `varchar(64)` | 不可 | 集計式版。 |
| `source_watermark` | `timestamptz` | 不可 | 集計元データの取込境界。 |
| `computed_at` | `timestamptz` | 不可 | 集計時刻。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, document_id, owner_department_id_snapshot, usage_date, metric`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, document_id)` → `documents(organization_id, id)`
- `(organization_id, owner_department_id_snapshot)` → `departments(organization_id, id)`

DBチェック: `metric_value >= 0` / `metric IN ('document_views','cited_answers')`。

検索インデックス: `organization_id, owner_department_id_snapshot, usage_date, document_id`。

業務制約・更新規則: cited_answersはoutcome=answeredの確定回答のみ。同じ回答で文書の3chunkを使っても1件。複数文書の件数を足した値を部署の質問数として表示しない。共有先の質問本文や利用者名は返さない。

## audit_events

権限・審査・削除等の改変を制限した業務監査。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `actor_user_id` | `uuid` | 可 | 人操作の主体。systemイベントではNULL。 |
| `actor_kind` | `varchar(16)` | 不可 | user / system。 |
| `acting_department_id` | `uuid` | 可 | 操作部署。 |
| `action` | `varchar(64)` | 不可 | 例 review.approve / document.delete / membership.revoke。 |
| `target_type` | `varchar(32)` | 不可 | 対象種別。 |
| `target_id` | `uuid` | 不可 | 対象ID。削除後も保持するためFKを張らない。 |
| `operation_key` | `varchar(128)` | 不可 | 業務操作の冪等な識別子。 |
| `before_revision` | `bigint` | 可 | 遷移前世代。 |
| `after_revision` | `bigint` | 可 | 遷移後世代。 |
| `details_json` | `jsonb` | 不可 | 状態・版・理由の安全な監査項目。本文・base64・token禁止。 |
| `occurred_at` | `timestamptz` | 不可 | 確定時刻。 |
| `expires_at` | `timestamptz` | 不可 | 監査保持期限。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, operation_key, action, target_id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, actor_user_id)` → `users(organization_id, id)`
- `(organization_id, acting_department_id)` → `departments(organization_id, id)`

DBチェック: `actor_kind IN ('user','system')` / `(actor_kind = 'user') = (actor_user_id IS NOT NULL)`。

検索インデックス: `organization_id, target_type, target_id, occurred_at` / `organization_id, acting_department_id, occurred_at`。

業務制約・更新規則: アプリ通常ロールにはINSERTのみ。削除担当は本文を消しても監査を保持期限まで保つ。UUID主体のマスターは無効化・匿名化しFK先を残す。

## outbox_events

業務更新と同時に確定する非同期配送予定。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `aggregate_type` | `varchar(32)` | 不可 | document / image / request 等。 |
| `aggregate_id` | `uuid` | 不可 | 対象ID。多態のためFKなし。 |
| `aggregate_revision` | `bigint` | 不可 | 当該更新世代。 |
| `event_type` | `varchar(64)` | 不可 | index.requested / ocr.requested / purge.requested 等。 |
| `payload_json` | `jsonb` | 不可 | 対象ID・版・設定参照。本文・画像バイトを入れない。 |
| `status` | `varchar(16)` | 不可 | pending / leased / dispatched / dead。 |
| `attempts` | `integer` | 不可 | 配送試行数。 |
| `available_at` | `timestamptz` | 不可 | 次回配送可能時刻。 |
| `lease_owner` | `varchar(128)` | 可 | 短期配送leaseの所有者。 |
| `lease_until` | `timestamptz` | 可 | 再取得可能になる時刻。 |
| `created_at` | `timestamptz` | 不可 | 業務確定時刻。 |
| `dispatched_at` | `timestamptz` | 可 | SQS受領確認時刻。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, aggregate_type, aggregate_id, aggregate_revision, event_type`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`

DBチェック: `status IN ('pending','leased','dispatched','dead')` / `aggregate_revision > 0 AND attempts >= 0`。

検索インデックス: `organization_id, status, available_at, id`。

業務制約・更新規則: DSQL tx内でSQS送信しない。短期leaseをCAS取得→送信→完了更新。重複配送前提で消費側は対象ID/世代に冪等。書込み後の配送起動と定期掃引を併用。

## idempotency_records

編集・申請・審査・削除APIの再送結果。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `actor_user_id` | `uuid` | 不可 | 認証済み実行者。 |
| `operation` | `varchar(64)` | 不可 | 操作種別。 |
| `request_key` | `varchar(128)` | 不可 | クライアントの冪等キー。 |
| `request_sha256` | `varchar(64)` | 不可 | 正規化入力hash。同一キー異内容は409。 |
| `result_type` | `varchar(32)` | 不可 | 結果の資源種別。 |
| `result_id` | `uuid` | 不可 | 確定した版・申請・削除ジョブ等。多態参照。 |
| `created_at` | `timestamptz` | 不可 | 結果確定時刻。 |
| `expires_at` | `timestamptz` | 不可 | キー保持期限。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, actor_user_id, operation, request_key`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, actor_user_id)` → `users(organization_id, id)`

検索インデックス: `organization_id, expires_at, id`。

業務制約・更新規則: 業務結果と同一トランザクションで確定。期限後も版UNIQUEや審査状態遷移で二重の意味的更新を防ぐ。再送結果を返す前にも現在認可を確認。

## deletion_jobs

論理削除後の段階的な物理削除。

| カラム | 型 | NULL | 内容 |
| --- | --- | --- | --- |
| `id` | `uuid` | 不可 | ランダムUUID。アプリが発行する主キー。 |
| `organization_id` | `uuid` | 不可 | 所属組織。認証済みコンテキストから決める。 |
| `document_id` | `uuid` | 不可 | 削除対象。最後までtombstone文書行を保持。 |
| `requested_by` | `uuid` | 不可 | 所有部署のリーダー等、削除権限者。 |
| `reason` | `text` | 不可 | 削除理由。 |
| `status` | `varchar(16)` | 不可 | waiting / purging / completed / failed / held。 |
| `purge_after` | `timestamptz` | 不可 | 保留期間後の物理削除可能時刻。 |
| `legal_hold` | `boolean` | 不可 | 保全理由によるpurge停止。 |
| `progress_json` | `jsonb` | 不可 | 索引・S3版・DB子テーブルごとの再開cursorと実績。 |
| `attempts` | `integer` | 不可 | 再実行回数。 |
| `created_at` | `timestamptz` | 不可 | 論理削除確定時刻。 |
| `completed_at` | `timestamptz` | 可 | 実体削除完了時刻。 |
| `error_code` | `varchar(64)` | 可 | 機密情報を含めない失敗分類。 |

主キー: `id`。

一意制約: `organization_id, id` / `organization_id, document_id`。

外部キー（すべてRESTRICT。認可は別途アプリで強制）:

- `(organization_id)` → `organizations(id)`
- `(organization_id, document_id)` → `documents(organization_id, id)`
- `(organization_id, requested_by)` → `users(organization_id, id)`

DBチェック: `status IN ('waiting','purging','completed','failed','held')` / `attempts >= 0` / `status <> 'completed' OR completed_at IS NOT NULL`。

検索インデックス: `organization_id, status, purge_after`。

業務制約・更新規則: 文書は直ちに利用停止。依存関係の末端から小分けpurgeし、大規模CASCADEを使わない。統計・監査は別保持。DSQLでは参照識別子と必要最小のhashをtombstoneとして残せる。
