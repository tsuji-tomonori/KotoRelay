-- draftsの正本と組織内参照整合性を定義する。
CREATE TABLE drafts (
    id varchar(36) NOT NULL,
    organization_id varchar(36) NOT NULL,
    document_id varchar(36) NOT NULL,
    body_key text NOT NULL,
    body_hash varchar(64) NOT NULL,
    placements text NOT NULL,
    revision bigint NOT NULL,
    updated_by varchar(36) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (organization_id, id),
    UNIQUE (organization_id, document_id),
    FOREIGN KEY (organization_id, document_id) REFERENCES documents (organization_id, id),
    FOREIGN KEY (organization_id, updated_by) REFERENCES users (organization_id, id),
    FOREIGN KEY (organization_id) REFERENCES organizations (id)
);
