<!-- 実装から生成。直接編集しない。入力SHA256: 209f2912c47883d8fdc722aafdde6cf403dff105c2efced6770337a06a320dd2 -->

# 競合を検出して下書きを保存 — sequence

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API
    participant D as PostgreSQLまたはDSQL
    participant S as S3実体
    participant M as Bedrock
    U->>A: PUT /api/documents/{document_id}/draft
    A->>D: 有効組織・所属を取得
    alt 認可条件が不成立
        A-->>U: 401または403または404
    else 許可
        A->>D: assets_get
        A->>D: departments_list
        A->>D: documents_get
        A->>D: documents_update
        A->>D: drafts_list
        A->>D: drafts_update
        A->>D: memberships_list
        A->>D: ocr_runs_get
        A->>D: organizations_fence
        A->>D: organizations_get
        A->>D: users_list
        A->>S: 内容ハッシュ実体を照合
        opt 実体欠落・ハッシュ不一致
            A-->>U: 利用不可・回答保留
        end
        A->>D: 必要な変更を確定（競合時rollback）
        A-->>U: 認可済み結果
    end
```

## 制御順序（関数内の行順）

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.Context.document | 90 | Return | doc |
| kotorelay.context.now | 18 | Return | datetime.now(UTC) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.operations.documents.functions.draft | 144 | Return | {'document': doc, 'body': ctx.objects.get(row.body_key, row.body_hash).decode(), 'revision': row.revision, 'placements': json.loads(row.placements)} |
| kotorelay.operations.documents.functions.save | 193 | Return | draft(ctx, doc.id) |
| kotorelay.operations.documents.functions.validate_placements | 154 | For | For |
| kotorelay.operations.documents.router.save_draft | 46 | Return | f.save(ctx, str(document_id), data) |
