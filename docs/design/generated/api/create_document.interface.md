<!-- 実装から生成。直接編集しない。入力SHA256: 8ddb6b8d66f674570acb431243c0b3f3887134895acc19f3980f35e395ebe090 -->

# 文書を作成 — interface

`POST /api/documents`

アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.jsonのcomponentsで解決します。

```json
{
  "operationId": "create_document",
  "requestBody": {
    "content": {
      "application/json": {
        "schema": {
          "$ref": "#/components/schemas/CreateDocument"
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
  "summary": "文書を作成",
  "tags": [
    "文書"
  ]
}
```

| 参照型 | 制約 |
| --- | --- |
| CreateDocument | {"properties": {"title": {"type": "string", "maxLength": 200, "minLength": 1, "title": "Title"}, "department_id": {"type": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", "title": "Department Id"}}, "additionalProperties": false, "type": "object", "required": ["title", "department_id"], "title": "CreateDocument"} |
| DocumentsRow | {"properties": {"id": {"type": "string", "title": "Id"}, "organization_id": {"type": "string", "title": "Organization Id"}, "department_id": {"type": "string", "title": "Department Id"}, "title": {"type": "string", "title": "Title"}, "created_by": {"type": "string", "title": "Created By"}, "visibility": {"type": "string", "title": "Visibility"}, "shared_departments": {"type": "string", "title": "Shared Departments"}, "status": {"type": "string", "title": "Status"}, "revision": {"type": "integer", "title": "Revision"}, "next_version": {"type": "integer", "title": "Next Version"}, "latest_version_id": {"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Latest Version Id"}, "updated_at": {"type": "string", "format": "date-time", "title": "Updated At"}}, "type": "object", "required": ["id", "organization_id", "department_id", "title", "created_by", "visibility", "shared_departments", "status", "revision", "next_version", "latest_version_id", "updated_at"], "title": "DocumentsRow", "description": "documentsのDDL由来の行型。"} |
| HTTPValidationError | {"properties": {"detail": {"items": {"$ref": "#/components/schemas/ValidationError"}, "type": "array", "title": "Detail"}}, "type": "object", "title": "HTTPValidationError"} |
