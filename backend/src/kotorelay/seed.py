"""ローカル専用の架空利用者を冪等に登録する。"""

from kotorelay.config import Settings
from kotorelay.context import stable_id
from kotorelay.db import Database
from kotorelay.errors import require
from kotorelay.generated import queries as q

PERSONAS = {
    "author": ("青木 はるか", "開発部", False, True, False, False),
    "reviewer": ("佐藤 れん", "開発部", False, False, True, False),
    "reader": ("田中 みお", "開発部", False, False, False, False),
    "leader": ("高橋 なお", "開発部", True, False, False, False),
    "operator": ("運用担当", "開発部", False, False, False, True),
    "other": ("他部署の利用者", "営業部", False, False, False, False),
}


def seed(settings: Settings) -> None:
    require(settings.mode == "local", "forbidden", 403)
    org = settings.organization_id
    with Database(settings).transaction() as db:
        if q.organizations_get(db, org, org):
            return
        q.organizations_insert(
            db,
            q.OrganizationsRow(
                id=org,
                organization_id=org,
                name="KotoRelay サンプル組織",
                revision=1,
                suspended=False,
            ),
        )
        for name in ["開発部", "営業部"]:
            q.departments_insert(
                db,
                q.DepartmentsRow(id=stable_id(name), organization_id=org, name=name, active=True),
            )
        for persona, (name, department, leader, author, reviewer, operator) in PERSONAS.items():
            user_id = stable_id(persona)
            q.users_insert(
                db,
                q.UsersRow(
                    id=user_id,
                    organization_id=org,
                    subject="demo-" + persona,
                    display_name=name,
                    active=True,
                    operator=operator,
                ),
            )
            q.memberships_insert(
                db,
                q.MembershipsRow(
                    id=stable_id(persona + department),
                    organization_id=org,
                    department_id=stable_id(department),
                    user_id=user_id,
                    leader=leader,
                    can_author=author,
                    can_review=reviewer,
                    active=True,
                ),
            )


def main() -> None:
    seed(Settings())


if __name__ == "__main__":
    main()
