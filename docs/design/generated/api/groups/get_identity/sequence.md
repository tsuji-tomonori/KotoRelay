<!-- 実装から生成。直接編集しない。入力SHA256: 4c18ae62a9b9de513581947abfc60f1ec45b9f631019a142a812724b4695a84b -->

# 本人と現在の所属権限を取得 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API
    participant D as PostgreSQLまたはDSQL
    participant S as S3実体
    participant M as Bedrock
    U->>A: GET /api/groups/me
    A->>D: 有効組織・所属を取得
    alt 認可条件が不成立
        A-->>U: 401または403または404
    else 許可
        A->>D: departments_list
        A->>D: memberships_list
        A->>D: organizations_get
        A->>D: users_list
        A->>D: 必要な変更を確定（競合時rollback）
        A-->>U: 認可済み結果
    end
```

**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.Context.member | 56 | Return | any((m.department_id == department_id for m in self.memberships)) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.operations.groups.functions.identity | 10 | Return | {'user': ctx.user, 'memberships': ctx.memberships, 'departments': [d for d in q.departments_list(ctx.db, ctx.org) if ctx.member(d.id)], 'directory': [d for d in q.departments_list(ctx.db, ctx.org) if d.active], 'mode': ctx.settings.mode} |
| kotorelay.operations.groups.router.get_identity | 17 | Return | f.identity(ctx) |
