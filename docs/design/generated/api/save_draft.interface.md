<!-- 実装から生成。直接編集しない。入力SHA256: 209f2912c47883d8fdc722aafdde6cf403dff105c2efced6770337a06a320dd2 -->

# 競合を検出して下書きを保存 — interface

`PUT /api/documents/{document_id}/draft`

アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.jsonのcomponentsで解決します。

```json
{
  "operationId": "save_draft",
  "parameters": [
    {
      "in": "path",
      "name": "document_id",
      "required": true,
      "schema": {
        "format": "uuid",
        "title": "Document Id",
        "type": "string"
      }
    }
  ],
  "requestBody": {
    "content": {
      "application/json": {
        "schema": {
          "$ref": "#/components/schemas/SaveDraft"
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
            "title": "Response Save Draft",
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
  "summary": "競合を検出して下書きを保存",
  "tags": [
    "文書"
  ]
}
```

| 参照型 | 制約 |
| --- | --- |
| HTTPValidationError | {"properties": {"detail": {"items": {"$ref": "#/components/schemas/ValidationError"}, "type": "array", "title": "Detail"}}, "type": "object", "title": "HTTPValidationError"} |
| SaveDraft | {"properties": {"title": {"type": "string", "maxLength": 200, "minLength": 1, "title": "Title"}, "body": {"type": "string", "maxLength": 100000, "title": "Body"}, "revision": {"type": "integer", "minimum": 1.0, "title": "Revision"}, "placements": {"items": {"$ref": "#/components/schemas/Placement"}, "type": "array", "maxItems": 10, "title": "Placements"}}, "additionalProperties": false, "type": "object", "required": ["title", "body", "revision"], "title": "SaveDraft"} |
