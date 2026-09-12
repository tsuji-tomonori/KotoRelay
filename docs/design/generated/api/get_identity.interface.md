<!-- 実装から生成。直接編集しない。入力SHA256: e3cb305ddf380bd9917bab7f5404c8ac54c8511b8d91b58e7192aa0d5991c3cf -->

# 本人と現在の所属権限を取得 — interface

`GET /api/groups/me`

アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.jsonのcomponentsで解決します。

```json
{
  "operationId": "get_identity",
  "responses": {
    "200": {
      "content": {
        "application/json": {
          "schema": {
            "additionalProperties": true,
            "title": "Response Get Identity",
            "type": "object"
          }
        }
      },
      "description": "Successful Response"
    }
  },
  "security": [
    {
      "HTTPBearer": []
    }
  ],
  "summary": "本人と現在の所属権限を取得",
  "tags": [
    "部署"
  ]
}
```

| 参照型 | 制約 |
| --- | --- |
