-- versionsの正本と組織内参照整合性を定義する。
CREATE TABLE versions (
    id varchar(36) NOT NULL,
    organization_id varchar(36) NOT NULL,
    document_id varchar(36) NOT NULL,
    number bigint NOT NULL,
    title text NOT NULL,
    body_key text NOT NULL,
    body_hash varchar(64) NOT NULL,
    manifest text NOT NULL,
    manifest_hash varchar(64) NOT NULL,
    created_by varchar(36) NOT NULL,
    created_at timestamptz NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (organization_id, id),
    UNIQUE (organization_id, document_id, id),
    UNIQUE (organization_id, document_id, number),
    FOREIGN KEY (organization_id, document_id) REFERENCES documents (organization_id, id),
    FOREIGN KEY (organization_id, created_by) REFERENCES users (organization_id, id),
    FOREIGN KEY (organization_id) REFERENCES organizations (id)
);
