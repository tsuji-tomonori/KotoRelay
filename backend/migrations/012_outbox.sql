-- outboxの正本と組織内参照整合性を定義する。
CREATE TABLE outbox (
    id varchar(36) NOT NULL,
    organization_id varchar(36) NOT NULL,
    document_id varchar(36) NOT NULL,
    version_id varchar(36),
    kind varchar(20) NOT NULL,
    status varchar(20) NOT NULL,
    attempts bigint NOT NULL,
    error_code text NOT NULL,
    created_at timestamptz NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (organization_id, id),
    FOREIGN KEY (organization_id, document_id) REFERENCES documents (organization_id, id),
    FOREIGN KEY (organization_id, document_id, version_id)
    REFERENCES versions (organization_id, document_id, id),
    FOREIGN KEY (organization_id) REFERENCES organizations (id)
);
