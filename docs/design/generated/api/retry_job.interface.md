<!-- 実装から生成。直接編集しない。入力SHA256: f4209c4ed7b292c6ed57aa300cf25000f8931a1f59b1fb43cfeb436b1d949dbe -->

# 反映ジョブを再処理 — interface

`POST /api/operations/jobs/{job_id}`

アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.jsonのcomponentsで解決します。

```json
{
  "operationId": "retry_job",
  "parameters": [
    {
      "in": "path",
      "name": "job_id",
      "required": true,
      "schema": {
        "format": "uuid",
        "title": "Job Id",
        "type": "string"
      }
    }
  ],
  "responses": {
    "200": {
      "content": {
        "application/json": {
          "schema": {
            "$ref": "#/components/schemas/OutboxRow"
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
  "summary": "反映ジョブを再処理",
  "tags": [
    "運用"
  ]
}
```

| 参照型 | 制約 |
| --- | --- |
| HTTPValidationError | {"properties": {"detail": {"items": {"$ref": "#/components/schemas/ValidationError"}, "type": "array", "title": "Detail"}}, "type": "object", "title": "HTTPValidationError"} |
| OutboxRow | {"properties": {"id": {"type": "string", "title": "Id"}, "organization_id": {"type": "string", "title": "Organization Id"}, "document_id": {"type": "string", "title": "Document Id"}, "version_id": {"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Version Id"}, "kind": {"type": "string", "title": "Kind"}, "status": {"type": "string", "title": "Status"}, "attempts": {"type": "integer", "title": "Attempts"}, "error_code": {"type": "string", "title": "Error Code"}, "created_at": {"type": "string", "format": "date-time", "title": "Created At"}}, "type": "object", "required": ["id", "organization_id", "document_id", "version_id", "kind", "status", "attempts", "error_code", "created_at"], "title": "OutboxRow", "description": "outboxのDDL由来の行型。"} |
