"""「文書を作成」APIのHTTP境界を実リクエストで確認するサンプル。"""

from kotorelay.api_contract import ApiSample

SAMPLES = (
    ApiSample(
        name="認証情報がない要求の拒否",
        method="POST",
        path="/api/documents",
        expected_status=401,
        expected_fields={"code": "unauthenticated"},
    ),
)
