-- chunksの正本と組織内参照整合性を定義する。
CREATE TABLE chunks (
    id varchar(36) NOT NULL,
    organization_id varchar(36) NOT NULL,
    document_id varchar(36) NOT NULL,
    version_id varchar(36) NOT NULL,
    body_key text NOT NULL,
    sha256 varchar(64) NOT NULL,
    heading text NOT NULL,
    placements text NOT NULL,
    manifest_hash varchar(64) NOT NULL,
    ready boolean NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (organization_id, id),
    FOREIGN KEY (organization_id, document_id) REFERENCES documents (organization_id, id),
    FOREIGN KEY (organization_id, version_id) REFERENCES versions (organization_id, id),
    FOREIGN KEY (organization_id) REFERENCES organizations (id)
);
