"""DB portを置換し、業務単体試験ごとに独立したtransactionを用意する。"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from typing import TypeVar

import pytest
from fastapi.testclient import TestClient
from kotorelay.config import Settings
from kotorelay.db import Database
from kotorelay.main import create_app
from kotorelay.seed import seed
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class MemoryDatabase(Database):
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.tables: dict[str, dict[str, dict[str, object]]] = {}

    @contextmanager
    def transaction(self) -> Iterator[MemoryDatabase]:
        before = deepcopy(self.tables)
        try:
            yield self
        except Exception:
            self.tables = before
            raise

    def query(self, path: str, params: dict[str, object], model: type[T]) -> list[T]:
        table, _, operation = Path(path).stem.rpartition("_")
        rows = self.tables.get(table, {}).values()
        return [
            model.model_validate(deepcopy(r))
            for r in rows
            if r["organization_id"] == params["organization_id"]
            and (operation == "list" or r["id"] == params["id"])
        ]

    def execute(self, path: str, params: dict[str, object]) -> int:
        table, _, operation = Path(path).stem.rpartition("_")
        rows = self.tables.setdefault(table, {})
        key = str(params["id"])
        if operation == "fence":
            row = rows[key]
            if row["revision"] != params["revision"]:
                return 0
            row["revision"] = int(str(row["revision"])) + 1
        elif operation == "delete":
            rows.pop(key, None)
        elif operation == "insert":
            if key in rows:
                raise ValueError("一意制約違反")
            rows[key] = deepcopy(params)
        elif operation == "update":
            if key not in rows:
                return 0
            rows[key] = deepcopy(params)
        else:
            raise ValueError(operation)
        return 1


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(object_root=str(tmp_path / "objects"))


@pytest.fixture
def db(settings: Settings, monkeypatch: pytest.MonkeyPatch) -> MemoryDatabase:
    database = MemoryDatabase(settings)
    monkeypatch.setattr("kotorelay.seed.Database", lambda _: database)
    monkeypatch.setattr("kotorelay.runtime.Database", lambda _: database)
    seed(settings)
    return database


@pytest.fixture
def client(settings: Settings, db: MemoryDatabase) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as result:
        yield result
