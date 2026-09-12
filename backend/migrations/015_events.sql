-- eventsの正本と組織内参照整合性を定義する。
CREATE TABLE events (
    id varchar(36) NOT NULL,
    organization_id varchar(36) NOT NULL,
    user_id varchar(36) NOT NULL,
    department_id varchar(36) NOT NULL,
    document_id varchar(36),
    answer_id varchar(36),
    kind varchar(20) NOT NULL,
    outcome varchar(20) NOT NULL,
    created_at timestamptz NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (organization_id, id),
    FOREIGN KEY (organization_id, user_id) REFERENCES users (organization_id, id),
    FOREIGN KEY (organization_id, department_id) REFERENCES departments (organization_id, id),
    FOREIGN KEY (organization_id, document_id) REFERENCES documents (organization_id, id),
    FOREIGN KEY (organization_id, answer_id) REFERENCES answers (organization_id, id),
    FOREIGN KEY (organization_id) REFERENCES organizations (id)
);
