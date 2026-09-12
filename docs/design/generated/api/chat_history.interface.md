<!-- 実装から生成。直接編集しない。入力SHA256: f4209c4ed7b292c6ed57aa300cf25000f8931a1f59b1fb43cfeb436b1d949dbe -->

# 現行認可で会話履歴を再表示 — interface

`GET /api/chat/{conversation_id}`

アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.jsonのcomponentsで解決します。

```json
{
  "operationId": "chat_history",
  "parameters": [
    {
      "in": "path",
      "name": "conversation_id",
      "required": true,
      "schema": {
        "format": "uuid",
        "title": "Conversation Id",
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
              "$ref": "#/components/schemas/AnswerView"
            },
            "title": "Response Chat History",
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
  "summary": "現行認可で会話履歴を再表示",
  "tags": [
    "RAGチャット"
  ]
}
```

| 参照型 | 制約 |
| --- | --- |
| AnswerView | {"properties": {"id": {"type": "string", "title": "Id"}, "conversation_id": {"type": "string", "title": "Conversation Id"}, "question": {"type": "string", "title": "Question"}, "answer": {"type": "string", "title": "Answer"}, "status": {"type": "string", "title": "Status"}, "citations": {"items": {"$ref": "#/components/schemas/Citation"}, "type": "array", "title": "Citations"}, "model": {"type": "string", "title": "Model"}, "created_at": {"type": "string", "format": "date-time", "title": "Created At"}}, "type": "object", "required": ["id", "conversation_id", "question", "answer", "status", "citations", "model", "created_at"], "title": "AnswerView"} |
| HTTPValidationError | {"properties": {"detail": {"items": {"$ref": "#/components/schemas/ValidationError"}, "type": "array", "title": "Detail"}}, "type": "object", "title": "HTTPValidationError"} |
