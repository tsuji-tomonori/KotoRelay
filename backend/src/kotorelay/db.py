"""DB接続、parameter bindingとトランザクションだけを扱う。"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TypeVar, cast

import psycopg
from psycopg.rows import dict_row
from pydantic import BaseModel

from kotorelay.config import Settings

T = TypeVar("T", bound=BaseModel)
APP = Path(__file__).parent


class Database:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.connection: psycopg.Connection[dict[str, object]] | None = None

    def connect(self) -> psycopg.Connection[dict[str, object]]:
        if self.settings.mode == "aws":
            import aurora_dsql_psycopg as dsql

            return cast(
                psycopg.Connection[dict[str, object]],
                dsql.connect(
                    host=self.settings.dsql_host,
                    region=self.settings.region,
                    user=self.settings.dsql_user,
                    sslmode="verify-full",
                    row_factory=dict_row,
                    autocommit=False,
                ),
            )
        connection = psycopg.connect(self.settings.database_url, row_factory=dict_row)
        connection.isolation_level = psycopg.IsolationLevel.REPEATABLE_READ
        return connection

    @contextmanager
    def transaction(self) -> Iterator[Database]:
        with self.connect() as connection:
            self.connection = connection
            try:
                yield self
            finally:
                self.connection = None

    def query(self, path: str, params: dict[str, object], model: type[T]) -> list[T]:
        if self.connection is None:
            raise RuntimeError("トランザクションが開始されていません")
        cursor = self.connection.execute((APP / path).read_text(), params)
        return [model.model_validate(row) for row in cursor.fetchall()]

    def execute(self, path: str, params: dict[str, object]) -> int:
        if self.connection is None:
            raise RuntimeError("トランザクションが開始されていません")
        return self.connection.execute((APP / path).read_text(), params).rowcount
