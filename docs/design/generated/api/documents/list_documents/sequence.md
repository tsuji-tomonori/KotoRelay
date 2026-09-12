<!-- 実装から生成。直接編集しない。入力SHA256: 4c18ae62a9b9de513581947abfc60f1ec45b9f631019a142a812724b4695a84b -->

# 閲覧可能な文書を検索 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API
    participant D as PostgreSQLまたはDSQL
    participant S as S3実体
    participant M as Bedrock
    U->>A: GET /api/documents
    A->>D: 有効組織・所属を取得
    alt 認可条件が不成立
        A-->>U: 401または403または404
    else 許可
        A->>D: chunks_list
        A->>D: departments_list
        A->>D: documents_by_department
        A->>D: documents_list
        A->>D: memberships_list
        A->>D: organizations_get
        A->>D: submissions_list
        A->>D: users_list
        A->>D: versions_list
        A->>S: 内容ハッシュ実体を照合
        opt 実体欠落・ハッシュ不一致
            A-->>U: 利用不可・回答保留
        end
        A->>D: 必要な変更を確定（競合時rollback）
        A-->>U: 認可済み結果
    end
```

**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.Context.can_read | 70 | If | doc.status != 'active' or not self.memberships |
| kotorelay.context.Context.can_read | 71 | Return | False |
| kotorelay.context.Context.can_read | 72 | If | doc.visibility == 'organization' |
| kotorelay.context.Context.can_read | 73 | Return | True |
| kotorelay.context.Context.can_read | 74 | If | self.member(doc.department_id) |
| kotorelay.context.Context.can_read | 75 | Return | True |
| kotorelay.context.Context.can_read | 76 | Return | doc.visibility == 'selected' and any((self.member(department) for department in json.loads(doc.shared_departments))) |
| kotorelay.context.Context.permission | 59 | For | For |
| kotorelay.context.Context.permission | 60 | If | m.department_id == department_id |
| kotorelay.context.Context.permission | 61 | Return | {'author': m.can_author, 'review': m.can_review, 'manage': m.leader, 'draft': m.can_author or m.can_review}.get(operation, False) |
| kotorelay.context.Context.permission | 67 | Return | False |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.operations.documents.functions.document_page | 115 | For | For |
| kotorelay.operations.documents.functions.document_page | 138 | Return | {'items': items, 'has_next': len(docs) > limit} |
| kotorelay.operations.documents.functions.list_documents | 68 | If | department_id and scope in {'manage', 'work'} |
| kotorelay.operations.documents.functions.list_documents | 79 | If | scope == 'manage' |
| kotorelay.operations.documents.functions.list_documents | 81 | If | scope == 'work' |
| kotorelay.operations.documents.functions.list_documents | 98 | Return | sorted(docs, key=lambda d: d.updated_at, reverse=True)[offset:offset + limit] |
| kotorelay.operations.documents.router.list_documents | 29 | If | page |
| kotorelay.operations.documents.router.list_documents | 30 | Return | f.document_page(ctx, scope, offset, limit, search, department, status) |
| kotorelay.operations.documents.router.list_documents | 31 | Return | f.list_documents(ctx, scope, offset, limit, search, department, status) |
