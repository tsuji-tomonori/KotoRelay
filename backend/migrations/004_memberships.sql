-- membershipsの正本と組織内参照整合性を定義する。
CREATE TABLE memberships (
    id varchar(36) NOT NULL,
    organization_id varchar(36) NOT NULL,
    department_id varchar(36) NOT NULL,
    user_id varchar(36) NOT NULL,
    leader boolean NOT NULL,
    can_author boolean NOT NULL,
    can_review boolean NOT NULL,
    active boolean NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (organization_id, id),
    UNIQUE (organization_id, department_id, user_id),
    FOREIGN KEY (organization_id, department_id) REFERENCES departments (organization_id, id),
    FOREIGN KEY (organization_id, user_id) REFERENCES users (organization_id, id),
    FOREIGN KEY (organization_id) REFERENCES organizations (id)
);
