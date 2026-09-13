"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 37de596e94bf1cba5b681194f62f74a4e184089dea8a7f03cbf336c5c5913050
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    EventsRow,
)


class EventsGetParams(BaseModel):
    """events_getの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


class EventsGetRow(EventsRow):
    """events_getのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    user_id: str
    department_id: str
    document_id: str | None
    answer_id: str | None
    kind: str
    outcome: str
    created_at: datetime


def events_get(db: Database, params: EventsGetParams) -> list[EventsGetRow]:
    "現在の組織に属する指定の利用イベントについて、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を取得する。"
    return db.query(
        "operations/metrics/record_view/sql/001_events_get.sql", params.model_dump(), EventsGetRow
    )


class EventsInsertParams(BaseModel):
    """events_insertの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    user_id: str
    department_id: str
    document_id: str | None
    answer_id: str | None
    kind: str
    outcome: str
    created_at: datetime


def events_insert(db: Database, params: EventsInsertParams) -> int:
    "現在の組織の利用イベントとして、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を登録する。"
    return db.execute(
        "operations/metrics/record_view/sql/002_events_insert.sql", params.model_dump()
    )
