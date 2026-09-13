"""「審査状況を一覧」APIのHTTP境界を実リクエストで確認するサンプル。"""

from kotorelay.api_contract import ApiSample

SAMPLES = (
    ApiSample(
        name="認証情報がない要求の拒否",
        method="GET",
        path="/api/reviews",
        expected_status=401,
        expected_fields={"code": "unauthenticated"},
    ),
)
