"""「部署の所属権限を変更」APIのHTTP境界を実リクエストで確認するサンプル。"""

from kotorelay.api_contract import ApiSample

SAMPLES = (
    ApiSample(
        name="認証情報がない要求の拒否",
        method="PUT",
        path="/api/groups/memberships",
        expected_status=401,
        expected_fields={"code": "unauthenticated"},
    ),
)
