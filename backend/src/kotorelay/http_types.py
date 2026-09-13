"""HTTPで共有する冪等性ヘッダーの型を定義する。"""

from typing import Annotated
from uuid import UUID

from fastapi import Header

Key = Annotated[UUID, Header(alias="Idempotency-Key")]
