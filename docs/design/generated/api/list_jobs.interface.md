<!-- 実装から生成。直接編集しない。入力SHA256: f4209c4ed7b292c6ed57aa300cf25000f8931a1f59b1fb43cfeb436b1d949dbe -->

# 反映ジョブと失敗理由を確認 — interface

`GET /api/operations/jobs`

アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.jsonのcomponentsで解決します。

```json
{
  "operationId": "list_jobs",
  "responses": {
    "200": {
      "content": {
        "application/json": {
          "schema": {
            "items": {
              "$ref": "#/components/schemas/OutboxRow"
            },
            "title": "Response List Jobs",
            "type": "array"
          }
        }
      },
      "description": "Successful Response"
    }
  },
  "security": [
    {
      "HTTPBearer": []
    }
  ],
  "summary": "反映ジョブと失敗理由を確認",
  "tags": [
    "運用"
  ]
}
```

| 参照型 | 制約 |
| --- | --- |
| OutboxRow | {"properties": {"id": {"type": "string", "title": "Id"}, "organization_id": {"type": "string", "title": "Organization Id"}, "document_id": {"type": "string", "title": "Document Id"}, "version_id": {"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Version Id"}, "kind": {"type": "string", "title": "Kind"}, "status": {"type": "string", "title": "Status"}, "attempts": {"type": "integer", "title": "Attempts"}, "error_code": {"type": "string", "title": "Error Code"}, "created_at": {"type": "string", "format": "date-time", "title": "Created At"}}, "type": "object", "required": ["id", "organization_id", "document_id", "version_id", "kind", "status", "attempts", "error_code", "created_at"], "title": "OutboxRow", "description": "outboxのDDL由来の行型。"} |
