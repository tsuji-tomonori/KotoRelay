<!-- 実装から生成。直接編集しない。入力SHA256: f4209c4ed7b292c6ed57aa300cf25000f8931a1f59b1fb43cfeb436b1d949dbe -->

# 部署の所属権限を変更 — interface

`PUT /api/groups/memberships`

アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.jsonのcomponentsで解決します。

```json
{
  "operationId": "change_membership",
  "requestBody": {
    "content": {
      "application/json": {
        "schema": {
          "$ref": "#/components/schemas/ChangeMembership"
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
            "$ref": "#/components/schemas/MembershipsRow"
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
  "summary": "部署の所属権限を変更",
  "tags": [
    "部署"
  ]
}
```

| 参照型 | 制約 |
| --- | --- |
| ChangeMembership | {"properties": {"user_id": {"type": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", "title": "User Id"}, "department_id": {"type": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", "title": "Department Id"}, "leader": {"type": "boolean", "title": "Leader", "default": false}, "can_author": {"type": "boolean", "title": "Can Author", "default": false}, "can_review": {"type": "boolean", "title": "Can Review", "default": false}, "active": {"type": "boolean", "title": "Active", "default": true}}, "additionalProperties": false, "type": "object", "required": ["user_id", "department_id"], "title": "ChangeMembership"} |
| HTTPValidationError | {"properties": {"detail": {"items": {"$ref": "#/components/schemas/ValidationError"}, "type": "array", "title": "Detail"}}, "type": "object", "title": "HTTPValidationError"} |
| MembershipsRow | {"properties": {"id": {"type": "string", "title": "Id"}, "organization_id": {"type": "string", "title": "Organization Id"}, "department_id": {"type": "string", "title": "Department Id"}, "user_id": {"type": "string", "title": "User Id"}, "leader": {"type": "boolean", "title": "Leader"}, "can_author": {"type": "boolean", "title": "Can Author"}, "can_review": {"type": "boolean", "title": "Can Review"}, "active": {"type": "boolean", "title": "Active"}}, "type": "object", "required": ["id", "organization_id", "department_id", "user_id", "leader", "can_author", "can_review", "active"], "title": "MembershipsRow", "description": "membershipsのDDL由来の行型。"} |
