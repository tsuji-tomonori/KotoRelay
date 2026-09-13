"""「manifestを確認して承認・却下」APIのHTTP境界を実リクエストで確認するサンプル。"""

from kotorelay.api_contract import ApiSample

SAMPLES = (
    ApiSample(
        name="認証情報がない要求の拒否",
        method="POST",
        path="/api/reviews/00000000-0000-0000-0000-000000000001/decision",
        expected_status=401,
        expected_fields={"code": "unauthenticated"},
    ),
)
