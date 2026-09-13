"""「本人と現在の所属権限を取得」APIのHTTP境界を実リクエストで確認するサンプル。"""

from kotorelay.api_contract import ApiSample

SAMPLES = (
    ApiSample(
        name="認証情報がない要求の拒否",
        method="GET",
        path="/api/groups/me",
        expected_status=401,
        expected_fields={"code": "unauthenticated"},
    ),
)
