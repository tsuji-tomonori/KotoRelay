-- answersの正本と組織内参照整合性を定義する。
CREATE TABLE answers (
    id varchar(36) NOT NULL,
    organization_id varchar(36) NOT NULL,
    conversation_id varchar(36) NOT NULL,
    user_id varchar(36) NOT NULL,
    department_id varchar(36) NOT NULL,
    question_key text NOT NULL,
    answer_key text NOT NULL,
    evidence text NOT NULL,
    status varchar(20) NOT NULL,
    model text NOT NULL,
    created_at timestamptz NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (organization_id, id),
    FOREIGN KEY (organization_id, conversation_id) REFERENCES conversations (organization_id, id),
    FOREIGN KEY (organization_id, user_id) REFERENCES users (organization_id, id),
    FOREIGN KEY (organization_id, department_id) REFERENCES departments (organization_id, id),
    FOREIGN KEY (organization_id) REFERENCES organizations (id)
);
