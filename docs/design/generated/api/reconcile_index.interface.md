<!-- 実装から生成。直接編集しない。入力SHA256: 209f2912c47883d8fdc722aafdde6cf403dff105c2efced6770337a06a320dd2 -->

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
