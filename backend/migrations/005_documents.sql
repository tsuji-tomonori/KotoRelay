-- documentsの正本と組織内参照整合性を定義する。
CREATE TABLE documents (
    id varchar(36) NOT NULL,
    organization_id varchar(36) NOT NULL,
    department_id varchar(36) NOT NULL,
    title text NOT NULL,
    created_by varchar(36) NOT NULL,
    visibility varchar(20) NOT NULL,
    shared_departments text NOT NULL,
    status varchar(20) NOT NULL,
    revision bigint NOT NULL,
    next_version bigint NOT NULL,
    latest_version_id varchar(36),
    updated_at timestamptz NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (organization_id, id),
    FOREIGN KEY (organization_id, department_id) REFERENCES departments (organization_id, id),
    FOREIGN KEY (organization_id, created_by) REFERENCES users (organization_id, id),
    CHECK (visibility IN ('department', 'selected', 'organization')),
    CHECK (status IN ('active', 'withdrawn', 'deleted')),
    FOREIGN KEY (organization_id) REFERENCES organizations (id)
);
