-- organizationsの正本と組織内参照整合性を定義する。
CREATE TABLE organizations (
    id varchar(36) NOT NULL,
    organization_id varchar(36) NOT NULL,
    name text NOT NULL,
    revision bigint NOT NULL,
    suspended boolean NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (organization_id, id)
);
