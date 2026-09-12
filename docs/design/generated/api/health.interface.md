<!-- 実装から生成。直接編集しない。入力SHA256: e3cb305ddf380bd9917bab7f5404c8ac54c8511b8d91b58e7192aa0d5991c3cf -->

# 死活確認 — interface

`GET /api/health`

アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.jsonのcomponentsで解決します。

```json
{
  "operationId": "health",
  "responses": {
    "200": {
      "content": {
        "application/json": {
          "schema": {
            "additionalProperties": {
              "type": "string"
            },
            "title": "Response Health",
            "type": "object"
          }
        }
      },
      "description": "Successful Response"
    }
  },
  "summary": "死活確認",
  "tags": [
    "システム"
  ]
}
```

| 参照型 | 制約 |
| --- | --- |
