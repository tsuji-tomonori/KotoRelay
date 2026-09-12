<!-- 実装から生成。直接編集しない。入力SHA256: 209f2912c47883d8fdc722aafdde6cf403dff105c2efced6770337a06a320dd2 -->

# OCRを訂正し新しいrunを保存 — interface

`POST /api/images/{asset_id}/ocr`

アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.jsonのcomponentsで解決します。

```json
{
  "operationId": "correct_ocr",
  "parameters": [
    {
      "in": "path",
      "name": "asset_id",
      "required": true,
      "schema": {
        "format": "uuid",
        "title": "Asset Id",
        "type": "string"
      }
    }
  ],
  "requestBody": {
    "content": {
      "application/json": {
        "schema": {
          "$ref": "#/components/schemas/OcrCorrection"
        }
      }
    },
    "required": true
  },
  "responses": {
    "200": {
      "content": {
        "application/json": {
          "schema": {
            "additionalProperties": true,
            "title": "Response Correct Ocr",
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
  "summary": "OCRを訂正し新しいrunを保存",
  "tags": [
    "画像・OCR"
  ]
}
```

| 参照型 | 制約 |
| --- | --- |
| HTTPValidationError | {"properties": {"detail": {"items": {"$ref": "#/components/schemas/ValidationError"}, "type": "array", "title": "Detail"}}, "type": "object", "title": "HTTPValidationError"} |
| OcrCorrection | {"properties": {"regions": {"items": {"$ref": "#/components/schemas/Region"}, "type": "array", "maxItems": 1000, "title": "Regions"}, "confirmed": {"type": "boolean", "title": "Confirmed"}}, "additionalProperties": false, "type": "object", "required": ["regions", "confirmed"], "title": "OcrCorrection"} |
