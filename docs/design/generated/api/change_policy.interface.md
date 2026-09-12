<!-- 実装から生成。直接編集しない。入力SHA256: 209f2912c47883d8fdc722aafdde6cf403dff105c2efced6770337a06a320dd2 -->

# リーダーが公開範囲・公開停止・削除を管理 — interface

`PUT /api/documents/{document_id}/policy`

アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.jsonのcomponentsで解決します。

```json
{
  "operationId": "change_policy",
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
          "$ref": "#/components/schemas/ChangePolicy"
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
            "$ref": "#/components/schemas/DocumentsRow"
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
  "summary": "リーダーが公開範囲・公開停止・削除を管理",
  "tags": [
    "文書"
  ]
}
```

| 参照型 | 制約 |
| --- | --- |
| ChangePolicy | {"properties": {"reason": {"type": "string", "maxLength": 2000, "title": "Reason", "default": ""}, "revision": {"type": "integer", "minimum": 1.0, "title": "Revision"}, "visibility": {"type": "string", "enum": ["department", "selected", "organization"], "title": "Visibility"}, "shared_departments": {"items": {"type": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"}, "type": "array", "maxItems": 30, "title": "Shared Departments"}, "status": {"type": "string", "enum": ["active", "withdrawn", "deleted"], "title": "Status"}}, "additionalProperties": false, "type": "object", "required": ["revision", "visibility", "status"], "title": "ChangePolicy"} |
| DocumentsRow | {"properties": {"id": {"type": "string", "title": "Id"}, "organization_id": {"type": "string", "title": "Organization Id"}, "department_id": {"type": "string", "title": "Department Id"}, "title": {"type": "string", "title": "Title"}, "created_by": {"type": "string", "title": "Created By"}, "visibility": {"type": "string", "title": "Visibility"}, "shared_departments": {"type": "string", "title": "Shared Departments"}, "status": {"type": "string", "title": "Status"}, "revision": {"type": "integer", "title": "Revision"}, "next_version": {"type": "integer", "title": "Next Version"}, "latest_version_id": {"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Latest Version Id"}, "updated_at": {"type": "string", "format": "date-time", "title": "Updated At"}}, "type": "object", "required": ["id", "organization_id", "department_id", "title", "created_by", "visibility", "shared_departments", "status", "revision", "next_version", "latest_version_id", "updated_at"], "title": "DocumentsRow", "description": "documentsのDDL由来の行型。"} |
| HTTPValidationError | {"properties": {"detail": {"items": {"$ref": "#/components/schemas/ValidationError"}, "type": "array", "title": "Detail"}}, "type": "object", "title": "HTTPValidationError"} |
