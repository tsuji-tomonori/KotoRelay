"""「最新承認版の根拠で回答」APIのHTTP境界を実リクエストで確認するサンプル。"""

from kotorelay.api_contract import ApiSample

SAMPLES = (
    ApiSample(
        name="認証情報がない要求の拒否",
        method="POST",
        path="/api/chat",
        expected_status=401,
        expected_fields={"code": "unauthenticated"},
    ),
)
