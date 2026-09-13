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
    """Given: 実PostgreSQLで文書と利用者を準備している。
    When: 申請・承認・索引反映・質問をHTTPで実行する。
    Then: 承認版を引用して回答し、他部署の直接閲覧は404となる。
    """
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
    """Given: 異なる文書に属する版が実DBにある。
    When: 別文書の版を参照するチャンクを保存する。
    Then: 外部キー制約が拒否し、誤った関連を保存しない。
    """
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
    """Given: 2接続が同じ組織の更新前状態を読んでいる。
    When: 一方を確定後、もう一方も同じ状態で更新する。
    Then: 後続更新は競合し、確定済みの1回分だけ保存番号が増える。
    """
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
    """Given: 実PostgreSQLに複数部署と文書がある。
    When: 部署別の管理一覧を少ない件数で取得する。
    Then: 実SQLでも部署を先に絞り、権限のない用途は403で拒否する。
    """
    from test_ui_contract import department_page_case

    with TestClient(create_app(postgres)) as client:
        department_page_case(client)


def test_成功応答の送信時には別接続から保存済み文書が見える(postgres):
    """Given: 実PostgreSQLを使うAPIの応答送信を観測できる。
    When: 文書作成の201応答が始まる時点で別接続から文書を読む。
    Then: 成功応答前にcommit済みで、作成した文書が別接続から見える。
    """
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
    """Given: 文書作成後のcommitで競合する接続を用意している。
    When: 文書作成を実行して保存状態を別接続から確認する。
    Then: 201を送らず409・conflictを返し、文書はrollbackされて残らない。
    """
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
