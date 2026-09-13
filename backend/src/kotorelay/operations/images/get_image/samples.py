"""「現在の認可で画像を配信」APIのHTTP境界を実リクエストで確認するサンプル。"""

from kotorelay.api_contract import ApiSample

SAMPLES = (
    ApiSample(
        name="認証情報がない要求の拒否",
        method="GET",
        path="/api/images/00000000-0000-0000-0000-000000000001",
        expected_status=401,
        expected_fields={"code": "unauthenticated"},
    ),
)
