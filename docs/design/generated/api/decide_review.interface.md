<!-- 実装から生成。直接編集しない。入力SHA256: e3cb305ddf380bd9917bab7f5404c8ac54c8511b8d91b58e7192aa0d5991c3cf -->

# manifestを確認して承認・却下 — interface

`POST /api/reviews/{submission_id}/decision`

アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.jsonのcomponentsで解決します。

```json
{
  "operationId": "decide_review",
  "parameters": [
    {
      "in": "path",
      "name": "submission_id",
      "required": true,
      "schema": {
        "format": "uuid",
        "title": "Submission Id",
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
          "$ref": "#/components/schemas/Decide"
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
            "$ref": "#/components/schemas/SubmissionsRow"
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
  "summary": "manifestを確認して承認・却下",
  "tags": [
    "審査"
  ]
}
```

| 参照型 | 制約 |
| --- | --- |
| Decide | {"properties": {"manifest_hash": {"type": "string", "pattern": "^[0-9a-f]{64}$", "title": "Manifest Hash"}, "decision": {"type": "string", "enum": ["approved", "rejected"], "title": "Decision"}, "reason": {"type": "string", "maxLength": 2000, "title": "Reason", "default": ""}}, "additionalProperties": false, "type": "object", "required": ["manifest_hash", "decision"], "title": "Decide"} |
| HTTPValidationError | {"properties": {"detail": {"items": {"$ref": "#/components/schemas/ValidationError"}, "type": "array", "title": "Detail"}}, "type": "object", "title": "HTTPValidationError"} |
| SubmissionsRow | {"properties": {"id": {"type": "string", "title": "Id"}, "organization_id": {"type": "string", "title": "Organization Id"}, "document_id": {"type": "string", "title": "Document Id"}, "version_id": {"type": "string", "title": "Version Id"}, "requested_by": {"type": "string", "title": "Requested By"}, "status": {"type": "string", "title": "Status"}, "manifest_hash": {"type": "string", "title": "Manifest Hash"}, "decided_by": {"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Decided By"}, "reason": {"type": "string", "title": "Reason"}, "created_at": {"type": "string", "format": "date-time", "title": "Created At"}, "decided_at": {"anyOf": [{"type": "string", "format": "date-time"}, {"type": "null"}], "title": "Decided At"}}, "type": "object", "required": ["id", "organization_id", "document_id", "version_id", "requested_by", "status", "manifest_hash", "decided_by", "reason", "created_at", "decided_at"], "title": "SubmissionsRow", "description": "submissionsのDDL由来の行型。"} |
