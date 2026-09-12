<!-- 実装から生成。直接編集しない。入力SHA256: e3cb305ddf380bd9917bab7f5404c8ac54c8511b8d91b58e7192aa0d5991c3cf -->

# 版を確定して承認申請 — interface

`POST /api/documents/{document_id}/submissions`

アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.jsonのcomponentsで解決します。

```json
{
  "operationId": "submit_version",
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
    },
    {
      "in": "header",
      "name": "Idempotency-Key",
      "required": true,
      "schema": {
        "format": "uuid",
        "title": "Idempotency-Key",
        "type": "string"
      }
    }
  ],
  "requestBody": {
    "content": {
      "application/json": {
        "schema": {
          "$ref": "#/components/schemas/Submit"
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
            "$ref": "#/components/schemas/VersionsRow"
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
  "summary": "版を確定して承認申請",
  "tags": [
    "文書"
  ]
}
```

| 参照型 | 制約 |
| --- | --- |
| HTTPValidationError | {"properties": {"detail": {"items": {"$ref": "#/components/schemas/ValidationError"}, "type": "array", "title": "Detail"}}, "type": "object", "title": "HTTPValidationError"} |
| Submit | {"properties": {"revision": {"type": "integer", "minimum": 1.0, "title": "Revision"}}, "additionalProperties": false, "type": "object", "required": ["revision"], "title": "Submit"} |
| VersionsRow | {"properties": {"id": {"type": "string", "title": "Id"}, "organization_id": {"type": "string", "title": "Organization Id"}, "document_id": {"type": "string", "title": "Document Id"}, "number": {"type": "integer", "title": "Number"}, "title": {"type": "string", "title": "Title"}, "body_key": {"type": "string", "title": "Body Key"}, "body_hash": {"type": "string", "title": "Body Hash"}, "manifest": {"type": "string", "title": "Manifest"}, "manifest_hash": {"type": "string", "title": "Manifest Hash"}, "created_by": {"type": "string", "title": "Created By"}, "created_at": {"type": "string", "format": "date-time", "title": "Created At"}}, "type": "object", "required": ["id", "organization_id", "document_id", "number", "title", "body_key", "body_hash", "manifest", "manifest_hash", "created_by", "created_at"], "title": "VersionsRow", "description": "versionsのDDL由来の行型。"} |
