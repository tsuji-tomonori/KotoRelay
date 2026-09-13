"""「実閲覧を一意IDで記録」APIのHTTP境界を実リクエストで確認するサンプル。"""

from kotorelay.api_contract import ApiSample

SAMPLES = (
    ApiSample(
        name="認証情報がない要求の拒否",
        method="POST",
        path="/api/metrics/views/00000000-0000-0000-0000-000000000001",
        expected_status=401,
        expected_fields={"code": "unauthenticated"},
    ),
)
