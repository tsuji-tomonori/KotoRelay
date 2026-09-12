<!-- 実装から生成。直接編集しない。入力SHA256: 8ddb6b8d66f674570acb431243c0b3f3887134895acc19f3980f35e395ebe090 -->

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
