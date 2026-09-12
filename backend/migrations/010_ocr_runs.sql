-- ocr_runsの正本と組織内参照整合性を定義する。
CREATE TABLE ocr_runs (
    id varchar(36) NOT NULL,
    organization_id varchar(36) NOT NULL,
    document_id varchar(36) NOT NULL,
    asset_id varchar(36) NOT NULL,
    result_key text NOT NULL,
    result_hash varchar(64) NOT NULL,
    engine text NOT NULL,
    status varchar(20) NOT NULL,
    confirmed boolean NOT NULL,
    created_at timestamptz NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (organization_id, id),
    FOREIGN KEY (organization_id, document_id) REFERENCES documents (organization_id, id),
    FOREIGN KEY (organization_id, document_id, asset_id)
    REFERENCES assets (organization_id, document_id, id),
    FOREIGN KEY (organization_id) REFERENCES organizations (id)
);
