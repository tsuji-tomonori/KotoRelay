<!-- 実装から生成。直接編集しない。入力SHA256: 4c18ae62a9b9de513581947abfc60f1ec45b9f631019a142a812724b4695a84b -->

# 実閲覧を一意IDで記録 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API
    participant D as PostgreSQLまたはDSQL
    participant S as S3実体
    participant M as Bedrock
    U->>A: POST /api/metrics/views/{document_id}
    A->>D: 有効組織・所属を取得
    alt 認可条件が不成立
        A-->>U: 401または403または404
    else 許可
        A->>D: departments_list
        A->>D: documents_get
        A->>D: events_get
        A->>D: events_insert
        A->>D: memberships_list
        A->>D: organizations_fence
        A->>D: organizations_get
        A->>D: users_list
        A->>D: 必要な変更を確定（競合時rollback）
        A-->>U: 認可済み結果
    end
```

**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.Context.document | 90 | Return | doc |
| kotorelay.context.Context.member | 56 | Return | any((m.department_id == department_id for m in self.memberships)) |
| kotorelay.context.now | 18 | Return | datetime.now(UTC) |
| kotorelay.context.stable_id | 26 | Return | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.operations.metrics.functions.view | 18 | If | previous |
| kotorelay.operations.metrics.functions.view | 26 | Return | {'recorded': False} |
| kotorelay.operations.metrics.functions.view | 42 | Return | {'recorded': True} |
| kotorelay.operations.metrics.router.record_view | 17 | Return | f.view(ctx, str(document_id), data) |
