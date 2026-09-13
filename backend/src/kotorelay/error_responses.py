"""HTTP例外ハンドラと設計生成が共有する安全な応答の契約。"""

from __future__ import annotations

import psycopg
from pydantic import BaseModel, ConfigDict

from kotorelay.errors import Problem


class ErrorOutcome(BaseModel):
    """エラー応答のstatusと本文。相関IDはHTTP境界で付与する。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    status: int
    code: str
    message: str


INVALID_INPUT = ErrorOutcome(
    status=422, code="invalid_input", message="入力形式を確認してください。"
)
DB_CONFLICT = ErrorOutcome(
    status=409, code="conflict", message="競合しました。再読込してください。"
)
UNAVAILABLE = ErrorOutcome(status=503, code="unavailable", message="一時的に利用できません。")


def problem_outcome(error: Problem) -> ErrorOutcome:
    return ErrorOutcome(status=error.status, code=error.code, message=error.message)


def database_outcome(error: psycopg.Error) -> ErrorOutcome:
    return DB_CONFLICT if error.sqlstate in {"40001", "23505", "OC000", "OC001"} else UNAVAILABLE
