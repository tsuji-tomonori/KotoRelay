"""「死活確認」APIのHTTP境界を実リクエストで確認するサンプル。"""

from kotorelay.api_contract import ApiSample

SAMPLES = (
    ApiSample(
        name="死活確認の成功",
        method="GET",
        path="/api/health",
        expected_status=200,
        expected_fields={"status": "ok", "product": "KotoRelay"},
    ),
)
