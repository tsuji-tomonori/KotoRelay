-- idempotencyの正本と組織内参照整合性を定義する。
CREATE TABLE idempotency (
    id varchar(36) NOT NULL,
    organization_id varchar(36) NOT NULL,
    user_id varchar(36) NOT NULL,
    operation text NOT NULL,
    request_hash varchar(64) NOT NULL,
    response text NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (organization_id, id),
    FOREIGN KEY (organization_id, user_id) REFERENCES users (organization_id, id),
    FOREIGN KEY (organization_id) REFERENCES organizations (id)
);
