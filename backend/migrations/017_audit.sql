-- auditの正本と組織内参照整合性を定義する。
CREATE TABLE audit (
    id varchar(36) NOT NULL,
    organization_id varchar(36) NOT NULL,
    user_id varchar(36) NOT NULL,
    document_id varchar(36),
    version_id varchar(36),
    action varchar(30) NOT NULL,
    before_state text NOT NULL,
    after_state text NOT NULL,
    reason text NOT NULL,
    created_at timestamptz NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (organization_id, id),
    FOREIGN KEY (organization_id, user_id) REFERENCES users (organization_id, id),
    FOREIGN KEY (organization_id, document_id) REFERENCES documents (organization_id, id),
    FOREIGN KEY (organization_id, version_id) REFERENCES versions (organization_id, id),
    FOREIGN KEY (organization_id) REFERENCES organizations (id)
);
