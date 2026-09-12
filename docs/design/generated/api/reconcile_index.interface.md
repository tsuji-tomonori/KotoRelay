<!-- 実装から生成。直接編集しない。入力SHA256: e3cb305ddf380bd9917bab7f5404c8ac54c8511b8d91b58e7192aa0d5991c3cf -->

# 正本と索引の不一致を確認 — interface

`GET /api/operations/reconcile`

アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.jsonのcomponentsで解決します。

```json
{
  "operationId": "reconcile_index",
  "responses": {
    "200": {
      "content": {
        "application/json": {
          "schema": {
            "items": {
              "additionalProperties": {
                "type": "string"
              },
              "type": "object"
            },
            "title": "Response Reconcile Index",
            "type": "array"
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
  "summary": "正本と索引の不一致を確認",
  "tags": [
    "運用"
  ]
}
```

| 参照型 | 制約 |
| --- | --- |
