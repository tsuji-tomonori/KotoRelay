<!-- 実装から生成。直接編集しない。入力SHA256: e3cb305ddf380bd9917bab7f5404c8ac54c8511b8d91b58e7192aa0d5991c3cf -->

# 認可されたOCR領域を取得 — interface

`GET /api/images/ocr/{run_id}`

アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.jsonのcomponentsで解決します。

```json
{
  "operationId": "get_ocr",
  "parameters": [
    {
      "in": "path",
      "name": "run_id",
      "required": true,
      "schema": {
        "format": "uuid",
        "title": "Run Id",
        "type": "string"
      }
    },
    {
      "in": "query",
      "name": "version_id",
      "required": false,
      "schema": {
        "anyOf": [
          {
            "format": "uuid",
            "type": "string"
          },
          {
            "type": "null"
          }
        ],
        "title": "Version Id"
      }
    }
  ],
  "responses": {
    "200": {
      "content": {
        "application/json": {
          "schema": {
            "$ref": "#/components/schemas/OcrResult"
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
  "summary": "認可されたOCR領域を取得",
  "tags": [
    "画像・OCR"
  ]
}
```

| 参照型 | 制約 |
| --- | --- |
| HTTPValidationError | {"properties": {"detail": {"items": {"$ref": "#/components/schemas/ValidationError"}, "type": "array", "title": "Detail"}}, "type": "object", "title": "HTTPValidationError"} |
| OcrResult | {"properties": {"regions": {"items": {"$ref": "#/components/schemas/Region"}, "type": "array", "maxItems": 1000, "title": "Regions"}, "engine": {"type": "string", "maxLength": 100, "title": "Engine"}, "status": {"type": "string", "enum": ["ready", "failed"], "title": "Status"}}, "additionalProperties": false, "type": "object", "required": ["regions", "engine", "status"], "title": "OcrResult"} |
