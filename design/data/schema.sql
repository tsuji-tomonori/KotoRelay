-- KotoRelay / Aurora DSQL データモデル v0.2 / 2026-09-12
-- 設計案。実DSQLでは未適用。1 DDLずつautocommitで実行し、ASYNC jobの完了を確認する。
-- BEGINやmigration toolの全体transactionで包まない。GRANT/IAM・移行・初期データは別設計。
-- https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with-ddl.html

CREATE SCHEMA kotorelay;

-- 導入組織。初期は一組織。
CREATE TABLE kotorelay.organizations (
  id uuid NOT NULL,
  code varchar(64) NOT NULL,
  name varchar(200) NOT NULL,
  status varchar(16) NOT NULL,
  auth_revision bigint NOT NULL,
  report_timezone varchar(64) NOT NULL,
  created_at timestamptz NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (code),
  CONSTRAINT ck_01_01 CHECK (status IN ('active','suspended')),
  CONSTRAINT ck_01_02 CHECK (auth_revision > 0)
 );

-- Cognitoの本人とアプリ利用者の対応。
CREATE TABLE kotorelay.users (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  cognito_subject varchar(128) NOT NULL,
  display_name varchar(200) NOT NULL,
  status varchar(16) NOT NULL,
  auth_revision bigint NOT NULL,
  created_at timestamptz NOT NULL,
  disabled_at timestamptz,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, cognito_subject),
  CONSTRAINT ck_02_01 CHECK (status IN ('active','disabled')),
  CONSTRAINT ck_02_02 CHECK (auth_revision > 0),
  CONSTRAINT fk_02_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 部署。初期の公開・管理境界。
CREATE TABLE kotorelay.departments (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  code varchar(64) NOT NULL,
  name varchar(200) NOT NULL,
  status varchar(16) NOT NULL,
  auth_revision bigint NOT NULL,
  created_at timestamptz NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, code),
  CONSTRAINT ck_03_01 CHECK (status IN ('active','archived')),
  CONSTRAINT ck_03_02 CHECK (auth_revision > 0),
  CONSTRAINT fk_03_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 兼務を含む利用者と部署の所属・操作権限。
CREATE TABLE kotorelay.department_memberships (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  department_id uuid NOT NULL,
  user_id uuid NOT NULL,
  role varchar(16) NOT NULL,
  can_author boolean NOT NULL,
  can_review boolean NOT NULL,
  status varchar(16) NOT NULL,
  auth_revision bigint NOT NULL,
  joined_at timestamptz NOT NULL,
  revoked_at timestamptz,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, department_id, user_id),
  CONSTRAINT ck_04_01 CHECK (role IN ('member','leader')),
  CONSTRAINT ck_04_02 CHECK (status IN ('active','revoked')),
  CONSTRAINT ck_04_03 CHECK (auth_revision > 0),
  CONSTRAINT fk_04_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_04_02 FOREIGN KEY (organization_id, department_id) REFERENCES kotorelay.departments (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_04_03 FOREIGN KEY (organization_id, user_id) REFERENCES kotorelay.users (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 版をまたぐ文書ID、所有部署、現行認可。
CREATE TABLE kotorelay.documents (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  owner_department_id uuid NOT NULL,
  created_by uuid NOT NULL,
  visibility varchar(16) NOT NULL,
  search_scope_token uuid NOT NULL,
  status varchar(16) NOT NULL,
  next_version_no bigint NOT NULL,
  auth_revision bigint NOT NULL,
  row_revision bigint NOT NULL,
  created_at timestamptz NOT NULL,
  updated_at timestamptz NOT NULL,
  deleted_at timestamptz,
  deleted_by uuid,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, search_scope_token),
  CONSTRAINT ck_05_01 CHECK (visibility IN ('department','selected','organization')),
  CONSTRAINT ck_05_02 CHECK (status IN ('active','withdrawn','deleted')),
  CONSTRAINT ck_05_03 CHECK (next_version_no > 0 AND auth_revision > 0 AND row_revision > 0),
  CONSTRAINT ck_05_04 CHECK ((status = 'deleted' AND deleted_at IS NOT NULL AND deleted_by IS NOT NULL) OR (status <> 'deleted' AND deleted_at IS NULL AND deleted_by IS NULL)),
  CONSTRAINT fk_05_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_05_02 FOREIGN KEY (organization_id, owner_department_id) REFERENCES kotorelay.departments (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_05_03 FOREIGN KEY (organization_id, created_by) REFERENCES kotorelay.users (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_05_04 FOREIGN KEY (organization_id, deleted_by) REFERENCES kotorelay.users (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 文書を追加公開する部署。
CREATE TABLE kotorelay.document_department_grants (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  department_id uuid NOT NULL,
  created_by uuid NOT NULL,
  created_at timestamptz NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, document_id, department_id),
  CONSTRAINT fk_06_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_06_02 FOREIGN KEY (organization_id, document_id) REFERENCES kotorelay.documents (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_06_03 FOREIGN KEY (organization_id, department_id) REFERENCES kotorelay.departments (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_06_04 FOREIGN KEY (organization_id, created_by) REFERENCES kotorelay.users (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 本文と画像/OCR manifestを凍結した文書版。
CREATE TABLE kotorelay.document_versions (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  version_no bigint NOT NULL,
  title varchar(500) NOT NULL,
  body_object_key text NOT NULL,
  body_s3_version_id text NOT NULL,
  body_sha256 varchar(64) NOT NULL,
  manifest_object_key text NOT NULL,
  manifest_s3_version_id text NOT NULL,
  manifest_sha256 varchar(64) NOT NULL,
  freeze_status varchar(16) NOT NULL,
  image_count integer NOT NULL,
  created_by uuid NOT NULL,
  created_at timestamptz NOT NULL,
  sealed_at timestamptz,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, document_id, version_no),
  UNIQUE (organization_id, document_id, id),
  CONSTRAINT ck_07_01 CHECK (version_no > 0 AND image_count >= 0),
  CONSTRAINT ck_07_02 CHECK (freeze_status IN ('staging','sealed')),
  CONSTRAINT ck_07_03 CHECK ((freeze_status = 'sealed') = (sealed_at IS NOT NULL)),
  CONSTRAINT fk_07_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_07_02 FOREIGN KEY (organization_id, document_id) REFERENCES kotorelay.documents (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_07_03 FOREIGN KEY (organization_id, created_by) REFERENCES kotorelay.users (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 一文書一つの作業コピー。
CREATE TABLE kotorelay.document_drafts (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  base_version_id uuid,
  title varchar(500) NOT NULL,
  body_object_key text NOT NULL,
  body_s3_version_id text NOT NULL,
  body_sha256 varchar(64) NOT NULL,
  row_revision bigint NOT NULL,
  updated_by uuid NOT NULL,
  updated_at timestamptz NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, document_id),
  UNIQUE (organization_id, document_id, id),
  CONSTRAINT ck_08_01 CHECK (row_revision > 0),
  CONSTRAINT fk_08_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_08_02 FOREIGN KEY (organization_id, document_id) REFERENCES kotorelay.documents (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_08_03 FOREIGN KEY (organization_id, document_id, base_version_id) REFERENCES kotorelay.document_versions (organization_id, document_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_08_04 FOREIGN KEY (organization_id, updated_by) REFERENCES kotorelay.users (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 版ごとに一回の審査申請と最終決定。
CREATE TABLE kotorelay.review_requests (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  version_id uuid NOT NULL,
  requested_by uuid NOT NULL,
  requested_at timestamptz NOT NULL,
  manifest_sha256 varchar(64) NOT NULL,
  status varchar(16) NOT NULL,
  decided_by uuid,
  decided_at timestamptz,
  decision_reason text,
  policy_version varchar(64) NOT NULL,
  row_revision bigint NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, version_id),
  UNIQUE (organization_id, document_id, id),
  CONSTRAINT ck_09_01 CHECK (status IN ('pending','approved','rejected','withdrawn')),
  CONSTRAINT ck_09_02 CHECK (row_revision > 0),
  CONSTRAINT ck_09_03 CHECK ((status = 'pending' AND decided_by IS NULL AND decided_at IS NULL) OR (status <> 'pending' AND decided_by IS NOT NULL AND decided_at IS NOT NULL)),
  CONSTRAINT ck_09_04 CHECK (status <> 'rejected' OR (decision_reason IS NOT NULL AND length(trim(decision_reason)) > 0)),
  CONSTRAINT fk_09_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_09_02 FOREIGN KEY (organization_id, document_id, version_id) REFERENCES kotorelay.document_versions (organization_id, document_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_09_03 FOREIGN KEY (organization_id, requested_by) REFERENCES kotorelay.users (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_09_04 FOREIGN KEY (organization_id, decided_by) REFERENCES kotorelay.users (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 一文書一件の審査待ちを担保する予約行。
CREATE TABLE kotorelay.document_review_slots (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  review_request_id uuid NOT NULL,
  created_at timestamptz NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, document_id),
  UNIQUE (organization_id, review_request_id),
  CONSTRAINT fk_10_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_10_02 FOREIGN KEY (organization_id, document_id, review_request_id) REFERENCES kotorelay.review_requests (organization_id, document_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- アップロードされた画像原本。文書所有で不変。
CREATE TABLE kotorelay.image_assets (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  original_object_key text NOT NULL,
  original_s3_version_id text NOT NULL,
  original_sha256 varchar(64) NOT NULL,
  original_filename varchar(500) NOT NULL,
  media_type varchar(64) NOT NULL,
  byte_size bigint NOT NULL,
  status varchar(16) NOT NULL,
  uploaded_by uuid NOT NULL,
  created_at timestamptz NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, document_id, id),
  CONSTRAINT ck_11_01 CHECK (byte_size > 0),
  CONSTRAINT ck_11_02 CHECK (status IN ('quarantined','ready','rejected')),
  CONSTRAINT fk_11_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_11_02 FOREIGN KEY (organization_id, document_id) REFERENCES kotorelay.documents (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_11_03 FOREIGN KEY (organization_id, uploaded_by) REFERENCES kotorelay.users (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 正規化画像・モデル入力画像の不変な派生版。
CREATE TABLE kotorelay.image_variants (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  asset_id uuid NOT NULL,
  variant_kind varchar(16) NOT NULL,
  object_key text NOT NULL,
  s3_version_id text NOT NULL,
  sha256 varchar(64) NOT NULL,
  media_type varchar(32) NOT NULL,
  byte_size bigint NOT NULL,
  width_px integer NOT NULL,
  height_px integer NOT NULL,
  transform_json jsonb NOT NULL,
  processor_version varchar(128) NOT NULL,
  created_at timestamptz NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, document_id, asset_id, id),
  UNIQUE (organization_id, asset_id, variant_kind, processor_version),
  CONSTRAINT ck_12_01 CHECK (variant_kind IN ('canonical','model')),
  CONSTRAINT ck_12_02 CHECK (media_type IN ('image/png','image/jpeg')),
  CONSTRAINT ck_12_03 CHECK (byte_size > 0 AND width_px > 0 AND height_px > 0),
  CONSTRAINT fk_12_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_12_02 FOREIGN KEY (organization_id, document_id, asset_id) REFERENCES kotorelay.image_assets (organization_id, document_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 画像ごとのOCR実行・訂正結果の不変スナップショット。
CREATE TABLE kotorelay.ocr_runs (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  asset_id uuid NOT NULL,
  variant_id uuid NOT NULL,
  engine varchar(64) NOT NULL,
  engine_version varchar(128) NOT NULL,
  config_sha256 varchar(64) NOT NULL,
  source_run_id uuid,
  status varchar(16) NOT NULL,
  region_count integer NOT NULL,
  raw_result_key text,
  raw_result_s3_version_id text,
  result_sha256 varchar(64),
  review_status varchar(16) NOT NULL,
  reviewed_by uuid,
  reviewed_at timestamptz,
  error_code varchar(64),
  started_at timestamptz,
  finished_at timestamptz,
  created_at timestamptz NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, document_id, asset_id, id),
  CONSTRAINT ck_13_01 CHECK (status IN ('queued','running','succeeded','no_text','failed')),
  CONSTRAINT ck_13_02 CHECK (review_status IN ('unchecked','accepted','needs_fix')),
  CONSTRAINT ck_13_03 CHECK (region_count >= 0),
  CONSTRAINT ck_13_04 CHECK (status NOT IN ('succeeded','no_text') OR (result_sha256 IS NOT NULL AND finished_at IS NOT NULL)),
  CONSTRAINT ck_13_05 CHECK (review_status <> 'accepted' OR (reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL AND status IN ('succeeded','no_text'))),
  CONSTRAINT fk_13_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_13_02 FOREIGN KEY (organization_id, document_id, asset_id, variant_id) REFERENCES kotorelay.image_variants (organization_id, document_id, asset_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_13_03 FOREIGN KEY (organization_id, document_id, asset_id, source_run_id) REFERENCES kotorelay.ocr_runs (organization_id, document_id, asset_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_13_04 FOREIGN KEY (organization_id, reviewed_by) REFERENCES kotorelay.users (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- OCRの文字列・読み順・画像内座標。
CREATE TABLE kotorelay.ocr_regions (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  asset_id uuid NOT NULL,
  ocr_run_id uuid NOT NULL,
  region_no integer NOT NULL,
  reading_order integer NOT NULL,
  text_content text NOT NULL,
  x numeric(8,6) NOT NULL,
  y numeric(8,6) NOT NULL,
  width numeric(8,6) NOT NULL,
  height numeric(8,6) NOT NULL,
  polygon_json jsonb NOT NULL,
  confidence numeric(8,6),
  region_kind varchar(16) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, ocr_run_id, region_no),
  UNIQUE (organization_id, document_id, asset_id, ocr_run_id, id),
  CONSTRAINT ck_14_01 CHECK (region_no >= 0 AND reading_order >= 0),
  CONSTRAINT ck_14_02 CHECK (x >= 0 AND y >= 0 AND width > 0 AND height > 0 AND x + width <= 1 AND y + height <= 1),
  CONSTRAINT ck_14_03 CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
  CONSTRAINT ck_14_04 CHECK (region_kind IN ('line','word','paragraph')),
  CONSTRAINT fk_14_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_14_02 FOREIGN KEY (organization_id, document_id, asset_id, ocr_run_id) REFERENCES kotorelay.ocr_runs (organization_id, document_id, asset_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 下書きMarkdownへの画像挿入箇所。
CREATE TABLE kotorelay.draft_image_placements (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  draft_id uuid NOT NULL,
  asset_id uuid NOT NULL,
  ocr_run_id uuid,
  anchor_id uuid NOT NULL,
  ordinal integer NOT NULL,
  source_start_byte integer NOT NULL,
  source_end_byte integer NOT NULL,
  alt_text text NOT NULL,
  caption text,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, draft_id, anchor_id),
  CONSTRAINT ck_15_01 CHECK (ordinal >= 0 AND source_start_byte >= 0 AND source_end_byte > source_start_byte),
  CONSTRAINT fk_15_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_15_02 FOREIGN KEY (organization_id, document_id, draft_id) REFERENCES kotorelay.document_drafts (organization_id, document_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_15_03 FOREIGN KEY (organization_id, document_id, asset_id) REFERENCES kotorelay.image_assets (organization_id, document_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_15_04 FOREIGN KEY (organization_id, document_id, asset_id, ocr_run_id) REFERENCES kotorelay.ocr_runs (organization_id, document_id, asset_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 承認対象版に固定された画像配置とOCR。
CREATE TABLE kotorelay.version_image_placements (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  version_id uuid NOT NULL,
  asset_id uuid NOT NULL,
  ocr_run_id uuid NOT NULL,
  anchor_id uuid NOT NULL,
  ordinal integer NOT NULL,
  source_start_byte integer NOT NULL,
  source_end_byte integer NOT NULL,
  heading_path_json jsonb NOT NULL,
  alt_text text NOT NULL,
  caption text,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, version_id, anchor_id),
  UNIQUE (organization_id, document_id, version_id, id),
  UNIQUE (organization_id, document_id, version_id, id, asset_id, ocr_run_id),
  CONSTRAINT ck_16_01 CHECK (ordinal >= 0 AND source_start_byte >= 0 AND source_end_byte > source_start_byte),
  CONSTRAINT fk_16_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_16_02 FOREIGN KEY (organization_id, document_id, version_id) REFERENCES kotorelay.document_versions (organization_id, document_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_16_03 FOREIGN KEY (organization_id, document_id, asset_id, ocr_run_id) REFERENCES kotorelay.ocr_runs (organization_id, document_id, asset_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 承認版の検索索引を構築する世代と実行状態。
CREATE TABLE kotorelay.index_builds (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  version_id uuid NOT NULL,
  generation_no bigint NOT NULL,
  status varchar(16) NOT NULL,
  manifest_sha256 varchar(64) NOT NULL,
  search_scope_token uuid NOT NULL,
  pipeline_version varchar(128) NOT NULL,
  embedding_model_id varchar(200) NOT NULL,
  kb_job_id varchar(200),
  expected_chunk_count integer NOT NULL,
  verified_chunk_count integer NOT NULL,
  error_code varchar(64),
  created_at timestamptz NOT NULL,
  ready_at timestamptz,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, version_id, generation_no),
  UNIQUE (organization_id, document_id, version_id, id),
  CONSTRAINT ck_17_01 CHECK (generation_no > 0 AND expected_chunk_count >= 0 AND verified_chunk_count >= 0),
  CONSTRAINT ck_17_02 CHECK (status IN ('queued','processing','verifying','ready','failed','obsolete')),
  CONSTRAINT ck_17_03 CHECK (status <> 'ready' OR (ready_at IS NOT NULL AND expected_chunk_count > 0 AND expected_chunk_count = verified_chunk_count)),
  CONSTRAINT fk_17_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_17_02 FOREIGN KEY (organization_id, document_id, version_id) REFERENCES kotorelay.document_versions (organization_id, document_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 最新承認版とRAGで使える索引世代の参照。
CREATE TABLE kotorelay.document_publications (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  latest_approved_version_id uuid NOT NULL,
  active_index_build_id uuid,
  row_revision bigint NOT NULL,
  updated_at timestamptz NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, document_id),
  CONSTRAINT ck_18_01 CHECK (row_revision > 0),
  CONSTRAINT fk_18_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_18_02 FOREIGN KEY (organization_id, document_id, latest_approved_version_id) REFERENCES kotorelay.document_versions (organization_id, document_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_18_03 FOREIGN KEY (organization_id, document_id, latest_approved_version_id, active_index_build_id) REFERENCES kotorelay.index_builds (organization_id, document_id, version_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 検索単位のテキストと出所。
CREATE TABLE kotorelay.chunks (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  version_id uuid NOT NULL,
  index_build_id uuid NOT NULL,
  chunk_no integer NOT NULL,
  text_object_key text NOT NULL,
  text_s3_version_id text NOT NULL,
  text_sha256 varchar(64) NOT NULL,
  source_start_byte integer NOT NULL,
  source_end_byte integer NOT NULL,
  heading_path_json jsonb NOT NULL,
  token_count integer NOT NULL,
  vector_record_key varchar(200) NOT NULL,
  created_at timestamptz NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, index_build_id, chunk_no),
  UNIQUE (organization_id, document_id, version_id, id),
  CONSTRAINT ck_19_01 CHECK (chunk_no >= 0 AND token_count >= 0),
  CONSTRAINT ck_19_02 CHECK (source_start_byte >= 0 AND source_end_byte >= source_start_byte),
  CONSTRAINT fk_19_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_19_02 FOREIGN KEY (organization_id, document_id, version_id, index_build_id) REFERENCES kotorelay.index_builds (organization_id, document_id, version_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- チャンクと画像配置の多対多関係。
CREATE TABLE kotorelay.chunk_images (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  version_id uuid NOT NULL,
  chunk_id uuid NOT NULL,
  placement_id uuid NOT NULL,
  asset_id uuid NOT NULL,
  ocr_run_id uuid NOT NULL,
  link_reason varchar(24) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, chunk_id, placement_id),
  UNIQUE (organization_id, document_id, chunk_id, placement_id, asset_id, ocr_run_id),
  CONSTRAINT ck_20_01 CHECK (link_reason IN ('source_overlap','ocr_evidence','contextual')),
  CONSTRAINT fk_20_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_20_02 FOREIGN KEY (organization_id, document_id, version_id, chunk_id) REFERENCES kotorelay.chunks (organization_id, document_id, version_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_20_03 FOREIGN KEY (organization_id, document_id, version_id, placement_id, asset_id, ocr_run_id) REFERENCES kotorelay.version_image_placements (organization_id, document_id, version_id, id, asset_id, ocr_run_id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- チャンクに採用したOCR領域の正確な来歴。
CREATE TABLE kotorelay.chunk_ocr_regions (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  chunk_id uuid NOT NULL,
  placement_id uuid NOT NULL,
  asset_id uuid NOT NULL,
  ocr_run_id uuid NOT NULL,
  region_id uuid NOT NULL,
  text_start_char integer NOT NULL,
  text_end_char integer NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, chunk_id, placement_id, region_id, text_start_char),
  CONSTRAINT ck_21_01 CHECK (text_start_char >= 0 AND text_end_char > text_start_char),
  CONSTRAINT fk_21_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_21_02 FOREIGN KEY (organization_id, document_id, chunk_id, placement_id, asset_id, ocr_run_id) REFERENCES kotorelay.chunk_images (organization_id, document_id, chunk_id, placement_id, asset_id, ocr_run_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_21_03 FOREIGN KEY (organization_id, document_id, asset_id, ocr_run_id, region_id) REFERENCES kotorelay.ocr_regions (organization_id, document_id, asset_id, ocr_run_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 利用者所有の短期チャットセッション。
CREATE TABLE kotorelay.rag_conversations (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  owner_user_id uuid NOT NULL,
  acting_department_id uuid NOT NULL,
  created_at timestamptz NOT NULL,
  expires_at timestamptz NOT NULL,
  status varchar(16) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, id, owner_user_id, acting_department_id),
  CONSTRAINT ck_22_01 CHECK (status IN ('active','deleted','expired')),
  CONSTRAINT ck_22_02 CHECK (expires_at > created_at),
  CONSTRAINT fk_22_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_22_02 FOREIGN KEY (organization_id, owner_user_id) REFERENCES kotorelay.users (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_22_03 FOREIGN KEY (organization_id, acting_department_id) REFERENCES kotorelay.departments (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 一回のユーザー質問。利用数の基準。
CREATE TABLE kotorelay.rag_requests (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  conversation_id uuid NOT NULL,
  user_id uuid NOT NULL,
  acting_department_id uuid NOT NULL,
  idempotency_key varchar(128) NOT NULL,
  question_object_key text NOT NULL,
  question_s3_version_id text NOT NULL,
  question_sha256 varchar(64) NOT NULL,
  status varchar(16) NOT NULL,
  policy_version varchar(128) NOT NULL,
  retrieval_config_version varchar(128) NOT NULL,
  auth_snapshot_json jsonb NOT NULL,
  accepted_at timestamptz NOT NULL,
  completed_at timestamptz,
  error_code varchar(64),
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, user_id, idempotency_key),
  CONSTRAINT ck_23_01 CHECK (status IN ('accepted','running','answered','abstained','failed','cancelled')),
  CONSTRAINT fk_23_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_23_02 FOREIGN KEY (organization_id, conversation_id, user_id, acting_department_id) REFERENCES kotorelay.rag_conversations (organization_id, id, owner_user_id, acting_department_id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 確定した回答と根拠manifest。
CREATE TABLE kotorelay.rag_answers (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  request_id uuid NOT NULL,
  outcome varchar(16) NOT NULL,
  body_object_key text NOT NULL,
  body_s3_version_id text NOT NULL,
  body_sha256 varchar(64) NOT NULL,
  evidence_manifest_sha256 varchar(64) NOT NULL,
  auth_fence_json jsonb NOT NULL,
  finalized_at timestamptz NOT NULL,
  expires_at timestamptz NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, request_id),
  CONSTRAINT ck_24_01 CHECK (outcome IN ('answered','abstained')),
  CONSTRAINT ck_24_02 CHECK (expires_at > finalized_at),
  CONSTRAINT fk_24_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_24_02 FOREIGN KEY (organization_id, request_id) REFERENCES kotorelay.rag_requests (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 確定回答に使ったチャンク、引用、送信画像の記録。
CREATE TABLE kotorelay.rag_evidence (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  answer_id uuid NOT NULL,
  document_id uuid NOT NULL,
  version_id uuid NOT NULL,
  chunk_id uuid NOT NULL,
  citation_no integer NOT NULL,
  rank_no integer NOT NULL,
  owner_department_id_snapshot uuid NOT NULL,
  image_inputs_json jsonb NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, answer_id, chunk_id),
  UNIQUE (organization_id, answer_id, citation_no),
  CONSTRAINT ck_25_01 CHECK (citation_no > 0 AND rank_no > 0),
  CONSTRAINT fk_25_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_25_02 FOREIGN KEY (organization_id, answer_id) REFERENCES kotorelay.rag_answers (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_25_03 FOREIGN KEY (organization_id, document_id, version_id, chunk_id) REFERENCES kotorelay.chunks (organization_id, document_id, version_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_25_04 FOREIGN KEY (organization_id, owner_department_id_snapshot) REFERENCES kotorelay.departments (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 質問に紐づく各モデル呼出し。再試行も別記録。
CREATE TABLE kotorelay.model_invocations (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  request_id uuid NOT NULL,
  phase varchar(16) NOT NULL,
  attempt_no integer NOT NULL,
  model_id varchar(200) NOT NULL,
  input_tokens bigint,
  output_tokens bigint,
  image_count integer NOT NULL,
  image_bytes bigint NOT NULL,
  input_manifest_sha256 varchar(64) NOT NULL,
  input_manifest_object_key text NOT NULL,
  input_manifest_s3_version_id text NOT NULL,
  status varchar(16) NOT NULL,
  started_at timestamptz NOT NULL,
  finished_at timestamptz,
  provider_request_id varchar(200),
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, request_id, phase, attempt_no),
  CONSTRAINT ck_26_01 CHECK (phase IN ('rewrite','rerank','generate')),
  CONSTRAINT ck_26_02 CHECK (status IN ('started','succeeded','failed')),
  CONSTRAINT ck_26_03 CHECK (attempt_no > 0 AND image_count >= 0 AND image_bytes >= 0),
  CONSTRAINT ck_26_04 CHECK (input_tokens IS NULL OR input_tokens >= 0),
  CONSTRAINT ck_26_05 CHECK (output_tokens IS NULL OR output_tokens >= 0),
  CONSTRAINT fk_26_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_26_02 FOREIGN KEY (organization_id, request_id) REFERENCES kotorelay.rag_requests (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 二重計上を防ぐ利用イベントの正本。
CREATE TABLE kotorelay.usage_events (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  event_kind varchar(24) NOT NULL,
  dedup_key varchar(200) NOT NULL,
  actor_user_id uuid NOT NULL,
  acting_department_id uuid NOT NULL,
  document_id uuid,
  version_id uuid,
  owner_department_id_snapshot uuid,
  rag_request_id uuid,
  occurred_at timestamptz NOT NULL,
  ingested_at timestamptz NOT NULL,
  expires_at timestamptz NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, dedup_key),
  CONSTRAINT ck_27_01 CHECK (event_kind IN ('rag_accepted','rag_answered','rag_abstained','rag_failed','rag_cancelled','document_view')),
  CONSTRAINT ck_27_02 CHECK ((event_kind = 'document_view' AND document_id IS NOT NULL AND version_id IS NOT NULL AND owner_department_id_snapshot IS NOT NULL AND rag_request_id IS NULL) OR (event_kind <> 'document_view' AND rag_request_id IS NOT NULL AND document_id IS NULL AND version_id IS NULL AND owner_department_id_snapshot IS NULL)),
  CONSTRAINT fk_27_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_27_02 FOREIGN KEY (organization_id, actor_user_id) REFERENCES kotorelay.users (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_27_03 FOREIGN KEY (organization_id, acting_department_id) REFERENCES kotorelay.departments (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_27_04 FOREIGN KEY (organization_id, document_id, version_id) REFERENCES kotorelay.document_versions (organization_id, document_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_27_05 FOREIGN KEY (organization_id, owner_department_id_snapshot) REFERENCES kotorelay.departments (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_27_06 FOREIGN KEY (organization_id, rag_request_id) REFERENCES kotorelay.rag_requests (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 部署が消費したRAG・閲覧の再計算可能な日次集計。
CREATE TABLE kotorelay.department_daily_usage (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  department_id uuid NOT NULL,
  usage_date date NOT NULL,
  metric varchar(32) NOT NULL,
  metric_value bigint NOT NULL,
  aggregation_version varchar(64) NOT NULL,
  source_watermark timestamptz NOT NULL,
  computed_at timestamptz NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, department_id, usage_date, metric),
  CONSTRAINT ck_28_01 CHECK (metric_value >= 0),
  CONSTRAINT ck_28_02 CHECK (metric IN ('rag_accepted','rag_answered','rag_abstained','rag_failed','rag_cancelled','document_views','active_users')),
  CONSTRAINT fk_28_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_28_02 FOREIGN KEY (organization_id, department_id) REFERENCES kotorelay.departments (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 所有部署が確認する文書別の閲覧とRAG貢献。
CREATE TABLE kotorelay.document_daily_usage (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  owner_department_id_snapshot uuid NOT NULL,
  usage_date date NOT NULL,
  metric varchar(32) NOT NULL,
  metric_value bigint NOT NULL,
  aggregation_version varchar(64) NOT NULL,
  source_watermark timestamptz NOT NULL,
  computed_at timestamptz NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, document_id, owner_department_id_snapshot, usage_date, metric),
  CONSTRAINT ck_29_01 CHECK (metric_value >= 0),
  CONSTRAINT ck_29_02 CHECK (metric IN ('document_views','cited_answers')),
  CONSTRAINT fk_29_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_29_02 FOREIGN KEY (organization_id, document_id) REFERENCES kotorelay.documents (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_29_03 FOREIGN KEY (organization_id, owner_department_id_snapshot) REFERENCES kotorelay.departments (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 権限・審査・削除等の改変を制限した業務監査。
CREATE TABLE kotorelay.audit_events (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  actor_user_id uuid,
  actor_kind varchar(16) NOT NULL,
  acting_department_id uuid,
  action varchar(64) NOT NULL,
  target_type varchar(32) NOT NULL,
  target_id uuid NOT NULL,
  operation_key varchar(128) NOT NULL,
  before_revision bigint,
  after_revision bigint,
  details_json jsonb NOT NULL,
  occurred_at timestamptz NOT NULL,
  expires_at timestamptz NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, operation_key, action, target_id),
  CONSTRAINT ck_30_01 CHECK (actor_kind IN ('user','system')),
  CONSTRAINT ck_30_02 CHECK ((actor_kind = 'user') = (actor_user_id IS NOT NULL)),
  CONSTRAINT fk_30_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_30_02 FOREIGN KEY (organization_id, actor_user_id) REFERENCES kotorelay.users (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_30_03 FOREIGN KEY (organization_id, acting_department_id) REFERENCES kotorelay.departments (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 業務更新と同時に確定する非同期配送予定。
CREATE TABLE kotorelay.outbox_events (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  aggregate_type varchar(32) NOT NULL,
  aggregate_id uuid NOT NULL,
  aggregate_revision bigint NOT NULL,
  event_type varchar(64) NOT NULL,
  payload_json jsonb NOT NULL,
  status varchar(16) NOT NULL,
  attempts integer NOT NULL,
  available_at timestamptz NOT NULL,
  lease_owner varchar(128),
  lease_until timestamptz,
  created_at timestamptz NOT NULL,
  dispatched_at timestamptz,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, aggregate_type, aggregate_id, aggregate_revision, event_type),
  CONSTRAINT ck_31_01 CHECK (status IN ('pending','leased','dispatched','dead')),
  CONSTRAINT ck_31_02 CHECK (aggregate_revision > 0 AND attempts >= 0),
  CONSTRAINT fk_31_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 編集・申請・審査・削除APIの再送結果。
CREATE TABLE kotorelay.idempotency_records (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  actor_user_id uuid NOT NULL,
  operation varchar(64) NOT NULL,
  request_key varchar(128) NOT NULL,
  request_sha256 varchar(64) NOT NULL,
  result_type varchar(32) NOT NULL,
  result_id uuid NOT NULL,
  created_at timestamptz NOT NULL,
  expires_at timestamptz NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, actor_user_id, operation, request_key),
  CONSTRAINT fk_32_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_32_02 FOREIGN KEY (organization_id, actor_user_id) REFERENCES kotorelay.users (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 論理削除後の段階的な物理削除。
CREATE TABLE kotorelay.deletion_jobs (
  id uuid NOT NULL,
  organization_id uuid NOT NULL,
  document_id uuid NOT NULL,
  requested_by uuid NOT NULL,
  reason text NOT NULL,
  status varchar(16) NOT NULL,
  purge_after timestamptz NOT NULL,
  legal_hold boolean NOT NULL,
  progress_json jsonb NOT NULL,
  attempts integer NOT NULL,
  created_at timestamptz NOT NULL,
  completed_at timestamptz,
  error_code varchar(64),
  PRIMARY KEY (id),
  UNIQUE (organization_id, id),
  UNIQUE (organization_id, document_id),
  CONSTRAINT ck_33_01 CHECK (status IN ('waiting','purging','completed','failed','held')),
  CONSTRAINT ck_33_02 CHECK (attempts >= 0),
  CONSTRAINT ck_33_03 CHECK (status <> 'completed' OR completed_at IS NOT NULL),
  CONSTRAINT fk_33_01 FOREIGN KEY (organization_id) REFERENCES kotorelay.organizations (id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_33_02 FOREIGN KEY (organization_id, document_id) REFERENCES kotorelay.documents (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT fk_33_03 FOREIGN KEY (organization_id, requested_by) REFERENCES kotorelay.users (organization_id, id) ON DELETE RESTRICT ON UPDATE RESTRICT
 );

-- 以下の各CREATE INDEX ASYNCも、別々のトランザクションで実行する。
-- 戻り値のjob IDで完了と索引の利用可能性を確認してから次工程へ進む。

CREATE INDEX ASYNC ix_04_01 ON kotorelay.department_memberships (organization_id, user_id, status, department_id);
CREATE INDEX ASYNC ix_05_01 ON kotorelay.documents (organization_id, owner_department_id, status, updated_at, id);
CREATE INDEX ASYNC ix_06_01 ON kotorelay.document_department_grants (organization_id, department_id, document_id);
CREATE INDEX ASYNC ix_09_01 ON kotorelay.review_requests (organization_id, status, requested_at, id);
CREATE INDEX ASYNC ix_11_01 ON kotorelay.image_assets (organization_id, document_id, status);
CREATE INDEX ASYNC ix_13_01 ON kotorelay.ocr_runs (organization_id, asset_id, created_at);
CREATE INDEX ASYNC ix_14_01 ON kotorelay.ocr_regions (organization_id, ocr_run_id, reading_order);
CREATE INDEX ASYNC ix_17_01 ON kotorelay.index_builds (organization_id, status, created_at);
CREATE INDEX ASYNC ix_22_01 ON kotorelay.rag_conversations (organization_id, owner_user_id, created_at);
CREATE INDEX ASYNC ix_23_01 ON kotorelay.rag_requests (organization_id, acting_department_id, accepted_at, id);
CREATE INDEX ASYNC ix_23_02 ON kotorelay.rag_requests (organization_id, conversation_id, accepted_at);
CREATE INDEX ASYNC ix_25_01 ON kotorelay.rag_evidence (organization_id, document_id, answer_id);
CREATE INDEX ASYNC ix_27_01 ON kotorelay.usage_events (organization_id, acting_department_id, occurred_at, id);
CREATE INDEX ASYNC ix_27_02 ON kotorelay.usage_events (organization_id, document_id, occurred_at, id);
CREATE INDEX ASYNC ix_27_03 ON kotorelay.usage_events (organization_id, ingested_at, id);
CREATE INDEX ASYNC ix_29_01 ON kotorelay.document_daily_usage (organization_id, owner_department_id_snapshot, usage_date, document_id);
CREATE INDEX ASYNC ix_30_01 ON kotorelay.audit_events (organization_id, target_type, target_id, occurred_at);
CREATE INDEX ASYNC ix_30_02 ON kotorelay.audit_events (organization_id, acting_department_id, occurred_at);
CREATE INDEX ASYNC ix_31_01 ON kotorelay.outbox_events (organization_id, status, available_at, id);
CREATE INDEX ASYNC ix_32_01 ON kotorelay.idempotency_records (organization_id, expires_at, id);
CREATE INDEX ASYNC ix_33_01 ON kotorelay.deletion_jobs (organization_id, status, purge_after);
