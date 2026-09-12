-- usersの正本と組織内参照整合性を定義する。
CREATE TABLE users (
    id varchar(36) NOT NULL,
    organization_id varchar(36) NOT NULL,
    subject text NOT NULL,
    display_name text NOT NULL,
    active boolean NOT NULL,
    operator boolean NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (organization_id, id),
    UNIQUE (organization_id, subject),
    FOREIGN KEY (organization_id) REFERENCES organizations (id)
);
