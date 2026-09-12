<!-- 実装から生成。直接編集しない。入力SHA256: 209f2912c47883d8fdc722aafdde6cf403dff105c2efced6770337a06a320dd2 -->

# 部署の利用数と文書貢献を集計 — interface

`GET /api/metrics/{department_id}`

アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.jsonのcomponentsで解決します。

```json
{
  "operationId": "department_metrics",
  "parameters": [
    {
      "in": "path",
      "name": "department_id",
      "required": true,
      "schema": {
        "format": "uuid",
        "title": "Department Id",
        "type": "string"
      }
    },
    {
      "in": "query",
      "name": "start",
      "required": true,
      "schema": {
        "format": "date-time",
        "title": "Start",
        "type": "string"
      }
    },
    {
      "in": "query",
      "name": "end",
      "required": true,
      "schema": {
        "format": "date-time",
        "title": "End",
        "type": "string"
      }
    }
  ],
  "responses": {
    "200": {
      "content": {
        "application/json": {
          "schema": {
            "additionalProperties": true,
            "title": "Response Department Metrics",
            "type": "object"
          }
        }
      },
      "description": "Successful Response"
    },
    "422": {
      "content": {
        "application/json": {
          "schema": {
            "$ref": "#/components/schemas/HTTPValidationError"
          }
        }
      },
      "description": "Validation Error"
    }
  },
  "security": [
    {
      "HTTPBearer": []
    }
  ],
  "summary": "部署の利用数と文書貢献を集計",
  "tags": [
    "利用統計"
  ]
}
```

| 参照型 | 制約 |
| --- | --- |
| HTTPValidationError | {"properties": {"detail": {"items": {"$ref": "#/components/schemas/ValidationError"}, "type": "array", "title": "Detail"}}, "type": "object", "title": "HTTPValidationError"} |
