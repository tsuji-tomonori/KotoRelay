"""「正本と索引の不一致を確認」APIのHTTP境界を実リクエストで確認するサンプル。"""

from kotorelay.api_contract import ApiSample

SAMPLES = (
    ApiSample(
        name="認証情報がない要求の拒否",
        method="GET",
        path="/api/operations/reconcile",
        expected_status=401,
        expected_fields={"code": "unauthenticated"},
    ),
)
