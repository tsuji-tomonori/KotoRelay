"""「自部署の所属を一覧」APIのHTTP境界を実リクエストで確認するサンプル。"""

from kotorelay.api_contract import ApiSample

SAMPLES = (
    ApiSample(
        name="認証情報がない要求の拒否",
        method="GET",
        path="/api/groups/00000000-0000-0000-0000-000000000001/members",
        expected_status=401,
        expected_fields={"code": "unauthenticated"},
    ),
)
