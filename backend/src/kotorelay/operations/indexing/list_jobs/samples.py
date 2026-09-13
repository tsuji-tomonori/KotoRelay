"""「反映ジョブと失敗理由を確認」APIのHTTP境界を実リクエストで確認するサンプル。"""

from kotorelay.api_contract import ApiSample

SAMPLES = (
    ApiSample(
        name="認証情報がない要求の拒否",
        method="GET",
        path="/api/operations/jobs",
        expected_status=401,
        expected_fields={"code": "unauthenticated"},
    ),
)
