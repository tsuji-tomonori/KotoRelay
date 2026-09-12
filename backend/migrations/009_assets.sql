-- assetsの正本と組織内参照整合性を定義する。
CREATE TABLE assets (
    id varchar(36) NOT NULL,
    organization_id varchar(36) NOT NULL,
    document_id varchar(36) NOT NULL,
    object_key text NOT NULL,
    sha256 varchar(64) NOT NULL,
    media_type varchar(20) NOT NULL,
    width bigint NOT NULL,
    height bigint NOT NULL,
    size bigint NOT NULL,
    created_at timestamptz NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (organization_id, id),
    FOREIGN KEY (organization_id, document_id) REFERENCES documents (organization_id, id),
    FOREIGN KEY (organization_id) REFERENCES organizations (id)
);
