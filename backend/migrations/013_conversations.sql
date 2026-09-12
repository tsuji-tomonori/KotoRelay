-- conversationsの正本と組織内参照整合性を定義する。
CREATE TABLE conversations (
    id varchar(36) NOT NULL,
    organization_id varchar(36) NOT NULL,
    user_id varchar(36) NOT NULL,
    created_at timestamptz NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (organization_id, id),
    FOREIGN KEY (organization_id, user_id) REFERENCES users (organization_id, id),
    FOREIGN KEY (organization_id) REFERENCES organizations (id)
);
