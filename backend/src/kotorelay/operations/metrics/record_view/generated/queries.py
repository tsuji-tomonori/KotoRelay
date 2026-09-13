"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 37de596e94bf1cba5b681194f62f74a4e184089dea8a7f03cbf336c5c5913050
"""

from kotorelay.db import Database
from kotorelay.generated.models import EventsRow


def events_get(db: Database, organization_id: str, id: str) -> list[EventsRow]:
    "現在の組織に属する指定の利用イベントについて、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を取得する。"
    return db.query(
        "operations/metrics/record_view/sql/events_get.sql",
        {"organization_id": organization_id, "id": id},
        EventsRow,
    )


def events_insert(db: Database, row: EventsRow) -> int:
    "現在の組織の利用イベントとして、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を登録する。"
    return db.execute("operations/metrics/record_view/sql/events_insert.sql", row.model_dump())
