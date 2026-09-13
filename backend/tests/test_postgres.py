"""実PostgreSQLで外部キー、rollback、競合検出を検証する。"""

from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
import query_helpers as q
from fastapi.testclient import TestClient
from kotorelay.config import Settings
from kotorelay.db import Database
from kotorelay.main import create_app
from kotorelay.seed import seed
from psycopg import sql
from psycopg.conninfo import make_conninfo
from test_workflow import ask, create, headers, published, submit


@pytest.fixture
def postgres(tmp_path):
    url = os.environ.get(
        "TEST_DATABASE_URL", "postgresql://kotorelay:kotorelay-local@localhost:55432/kotorelay"
    )
    schema = "test_" + uuid4().hex
    with psycopg.connect(url, autocommit=True) as connection:
        connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        try:
            connection.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema)))
            for path in sorted(Path("backend/migrations").glob("*.sql")):
                connection.execute(path.read_text())
            settings = Settings(
                database_url=make_conninfo(url, options="-csearch_path=" + schema),
                object_root=str(tmp_path / "objects"),
            )
            seed(settings)
            seed(settings)
            yield settings
        finally:
            connection.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))


def test_PostgreSQLで承認とoutboxと回答を一貫して確定する(postgres):
    with TestClient(create_app(postgres)) as client:
        doc, version = published(client)
        result = ask(client).json()
        assert (
            result["status"] == "answered" and result["citations"][0]["version_id"] == version["id"]
        )
        assert (
            client.get(f"/api/documents/{doc['id']}", headers=headers("other")).status_code == 404
        )


def test_DB自身が別文書への誤った版参照を拒否する(postgres):
    with TestClient(create_app(postgres)) as client:
        doc = create(client)
        other = create(client)
        version = submit(client, other)
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        with Database(postgres).transaction() as db:
            q.chunks_insert(
                db,
                q.ChunksInsertParams.model_validate(
                    q.ChunksRow(
                        id=str(uuid4()),
                        organization_id=postgres.organization_id,
                        document_id=doc["id"],
                        version_id=version["id"],
                        body_key="0" * 64,
                        sha256="0" * 64,
                        heading="本文",
                        placements="[]",
                        manifest_hash=version["manifest_hash"],
                        ready=False,
                    ),
                    from_attributes=True,
                ),
            )
    with Database(postgres).transaction() as db:
        assert all(
            row.document_id != doc["id"]
            for row in q.submissions_list(
                db, q.SubmissionsListParams(organization_id=postgres.organization_id)
            )
        )


def test_DBの競合時はtransaction全体がrollbackされる(postgres):
    org = postgres.organization_id
    with Database(postgres).transaction() as first:
        row = q.organizations_get(first, q.OrganizationsGetParams(organization_id=org, id=org))[0]
        with Database(postgres).transaction() as second:
            assert (
                q.organizations_fence(
                    second, q.OrganizationsFenceParams.model_validate(row, from_attributes=True)
                )
                == 1
            )
        with pytest.raises(psycopg.errors.SerializationFailure):
            q.organizations_fence(
                first, q.OrganizationsFenceParams.model_validate(row, from_attributes=True)
            )
    with Database(postgres).transaction() as check:
        assert (
            q.organizations_get(check, q.OrganizationsGetParams(organization_id=org, id=org))[
                0
            ].revision
            == row.revision + 1
        )


def test_実SQLで複数部署の管理一覧と権限を絞り込む(postgres):
    from test_ui_contract import department_page_case

    with TestClient(create_app(postgres)) as client:
        department_page_case(client)


def test_成功応答の送信時には別接続から保存済み文書が見える(postgres):
    app = create_app(postgres)
    observed = []
    title = "コミット済みの応答"

    async def checked(scope, receive, send):

        async def check_send(message):
            if message["type"] == "http.response.start" and message["status"] == 201:
                with Database(postgres).transaction() as db:
                    rows = q.documents_list(
                        db, q.DocumentsListParams(organization_id=postgres.organization_id)
                    )
                    observed.append(any(row.title == title for row in rows))
            await send(message)

        await app(scope, receive, check_send)

    with TestClient(checked) as client:
        department = client.get("/api/groups/me", headers=headers()).json()["departments"][0]["id"]
        result = client.post(
            "/api/documents", headers=headers(), json={"title": title, "department_id": department}
        )
        assert result.status_code == 201
    assert observed == [True]


def test_commit時の競合は成功応答を送らず409にしてrollbackする(postgres, monkeypatch):
    from contextlib import contextmanager

    app = create_app(postgres)
    with TestClient(app) as client:
        department = client.get("/api/groups/me", headers=headers()).json()["departments"][0]["id"]
        original = Database.transaction

        @contextmanager
        def conflict(self):
            with original(self) as db:
                yield db
                raise psycopg.errors.SerializationFailure("commit conflict")

        with monkeypatch.context() as patch:
            patch.setattr(Database, "transaction", conflict)
            result = client.post(
                "/api/documents",
                headers=headers(),
                json={"title": "競合して確定しない文書", "department_id": department},
            )
        assert result.status_code == 409
        assert result.json()["code"] == "conflict"
    with Database(postgres).transaction() as db:
        assert not q.documents_list(
            db, q.DocumentsListParams(organization_id=postgres.organization_id)
        )
