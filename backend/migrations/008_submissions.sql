-- submissionsの正本と組織内参照整合性を定義する。
CREATE TABLE submissions (
    id varchar(36) NOT NULL,
    organization_id varchar(36) NOT NULL,
    document_id varchar(36) NOT NULL,
    version_id varchar(36) NOT NULL,
    requested_by varchar(36) NOT NULL,
    status varchar(20) NOT NULL,
    manifest_hash varchar(64) NOT NULL,
    decided_by varchar(36),
    reason text NOT NULL,
    created_at timestamptz NOT NULL,
    decided_at timestamptz,
    PRIMARY KEY (id),
    UNIQUE (organization_id, id),
    UNIQUE (organization_id, version_id),
    FOREIGN KEY (organization_id, document_id) REFERENCES documents (organization_id, id),
    FOREIGN KEY (organization_id, version_id) REFERENCES versions (organization_id, id),
    FOREIGN KEY (organization_id, requested_by) REFERENCES users (organization_id, id),
    FOREIGN KEY (organization_id, decided_by) REFERENCES users (organization_id, id),
    CHECK (status IN ('pending', 'approved', 'rejected')),
    FOREIGN KEY (organization_id) REFERENCES organizations (id)
);
