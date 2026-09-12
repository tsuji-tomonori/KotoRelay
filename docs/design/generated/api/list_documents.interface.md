<!-- 実装から生成。直接編集しない。入力SHA256: f4209c4ed7b292c6ed57aa300cf25000f8931a1f59b1fb43cfeb436b1d949dbe -->

# 閲覧可能な文書を検索 — interface

`GET /api/documents`

アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.jsonのcomponentsで解決します。

```json
{
  "operationId": "list_documents",
  "parameters": [
    {
      "in": "query",
      "name": "scope",
      "required": false,
      "schema": {
        "default": "read",
        "enum": [
          "read",
          "work",
          "manage"
        ],
        "title": "Scope",
        "type": "string"
      }
    },
    {
      "in": "query",
      "name": "offset",
      "required": false,
      "schema": {
        "default": 0,
        "minimum": 0,
        "title": "Offset",
        "type": "integer"
      }
    },
    {
      "in": "query",
      "name": "limit",
      "required": false,
      "schema": {
        "default": 30,
        "maximum": 100,
        "minimum": 1,
        "title": "Limit",
        "type": "integer"
      }
    },
    {
      "in": "query",
      "name": "search",
      "required": false,
      "schema": {
        "default": "",
        "maxLength": 200,
        "title": "Search",
        "type": "string"
      }
    }
  ],
  "responses": {
    "200": {
      "content": {
        "application/json": {
          "schema": {
            "items": {
              "$ref": "#/components/schemas/DocumentsRow"
            },
            "title": "Response List Documents",
            "type": "array"
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
  "summary": "閲覧可能な文書を検索",
  "tags": [
    "文書"
  ]
}
```

| 参照型 | 制約 |
| --- | --- |
| DocumentsRow | {"properties": {"id": {"type": "string", "title": "Id"}, "organization_id": {"type": "string", "title": "Organization Id"}, "department_id": {"type": "string", "title": "Department Id"}, "title": {"type": "string", "title": "Title"}, "created_by": {"type": "string", "title": "Created By"}, "visibility": {"type": "string", "title": "Visibility"}, "shared_departments": {"type": "string", "title": "Shared Departments"}, "status": {"type": "string", "title": "Status"}, "revision": {"type": "integer", "title": "Revision"}, "next_version": {"type": "integer", "title": "Next Version"}, "latest_version_id": {"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Latest Version Id"}, "updated_at": {"type": "string", "format": "date-time", "title": "Updated At"}}, "type": "object", "required": ["id", "organization_id", "department_id", "title", "created_by", "visibility", "shared_departments", "status", "revision", "next_version", "latest_version_id", "updated_at"], "title": "DocumentsRow", "description": "documentsのDDL由来の行型。"} |
| HTTPValidationError | {"properties": {"detail": {"items": {"$ref": "#/components/schemas/ValidationError"}, "type": "array", "title": "Detail"}}, "type": "object", "title": "HTTPValidationError"} |
