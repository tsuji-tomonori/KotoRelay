-- departmentsの正本と組織内参照整合性を定義する。
CREATE TABLE departments (
    id varchar(36) NOT NULL,
    organization_id varchar(36) NOT NULL,
    name text NOT NULL,
    active boolean NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (organization_id, id),
    FOREIGN KEY (organization_id) REFERENCES organizations (id)
);
