"""「リーダーが公開範囲・公開停止・削除を管理」APIのHTTP境界を実リクエストで確認するサンプル。"""

from kotorelay.api_contract import ApiSample

SAMPLES = (
    ApiSample(
        name="認証情報がない要求の拒否",
        method="PUT",
        path="/api/documents/00000000-0000-0000-0000-000000000001/policy",
        expected_status=401,
        expected_fields={"code": "unauthenticated"},
    ),
)
