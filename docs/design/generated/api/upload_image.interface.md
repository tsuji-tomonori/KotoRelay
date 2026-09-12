<!-- 実装から生成。直接編集しない。入力SHA256: 209f2912c47883d8fdc722aafdde6cf403dff105c2efced6770337a06a320dd2 -->

# 画像を添付して位置付きOCRを実行 — interface

`POST /api/images/documents/{document_id}`

アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.jsonのcomponentsで解決します。

```json
{
  "operationId": "upload_image",
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
      "multipart/form-data": {
        "schema": {
          "$ref": "#/components/schemas/Body_upload_image"
        }
      }
    },
    "required": true
  },
  "responses": {
    "201": {
      "content": {
        "application/json": {
          "schema": {
            "additionalProperties": true,
            "title": "Response Upload Image",
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
  "summary": "画像を添付して位置付きOCRを実行",
  "tags": [
    "画像・OCR"
  ]
}
```

| 参照型 | 制約 |
| --- | --- |
| Body_upload_image | {"properties": {"file": {"type": "string", "contentMediaType": "application/octet-stream", "title": "File"}}, "type": "object", "required": ["file"], "title": "Body_upload_image"} |
| HTTPValidationError | {"properties": {"detail": {"items": {"$ref": "#/components/schemas/ValidationError"}, "type": "array", "title": "Detail"}}, "type": "object", "title": "HTTPValidationError"} |
