<!-- 実装から生成。直接編集しない。入力SHA256: 8ddb6b8d66f674570acb431243c0b3f3887134895acc19f3980f35e395ebe090 -->

# 最新承認版の根拠で回答 — interface

`POST /api/chat`

アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.jsonのcomponentsで解決します。

```json
{
  "operationId": "ask_question",
  "parameters": [
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
          "$ref": "#/components/schemas/Ask"
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
            "$ref": "#/components/schemas/AnswerView"
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
  "summary": "最新承認版の根拠で回答",
  "tags": [
    "RAGチャット"
  ]
}
```

| 参照型 | 制約 |
| --- | --- |
| AnswerView | {"properties": {"id": {"type": "string", "title": "Id"}, "conversation_id": {"type": "string", "title": "Conversation Id"}, "question": {"type": "string", "title": "Question"}, "answer": {"type": "string", "title": "Answer"}, "status": {"type": "string", "title": "Status"}, "citations": {"items": {"$ref": "#/components/schemas/Citation"}, "type": "array", "title": "Citations"}, "model": {"type": "string", "title": "Model"}, "created_at": {"type": "string", "format": "date-time", "title": "Created At"}}, "type": "object", "required": ["id", "conversation_id", "question", "answer", "status", "citations", "model", "created_at"], "title": "AnswerView"} |
| Ask | {"properties": {"question": {"type": "string", "maxLength": 2000, "minLength": 1, "title": "Question"}, "department_id": {"type": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", "title": "Department Id"}, "conversation_id": {"anyOf": [{"type": "string", "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"}, {"type": "null"}], "title": "Conversation Id"}}, "additionalProperties": false, "type": "object", "required": ["question", "department_id"], "title": "Ask"} |
| HTTPValidationError | {"properties": {"detail": {"items": {"$ref": "#/components/schemas/ValidationError"}, "type": "array", "title": "Detail"}}, "type": "object", "title": "HTTPValidationError"} |
