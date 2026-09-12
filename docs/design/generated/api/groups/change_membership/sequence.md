<!-- 実装から生成。直接編集しない。入力SHA256: 31de213f242d3d7bf0d4f5957d4ef327aaacb2267a973d8e0adce1f1531ac7e1 -->

# 部署の所属権限を変更 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API
    participant D as PostgreSQLまたはDSQL
    participant S as S3実体
    participant M as Bedrock
    U->>A: PUT /api/groups/memberships
    A->>D: 有効組織・所属を取得
    alt 認可条件が不成立
        A-->>U: 401または403または404
    else 許可
        A->>D: 現在の組織の監査記録として、操作した利用者・対象・変更前後の状態・理由を登録する。
        A->>D: 現在の組織に属する指定の部署について、部署名と有効状態を取得する。
        A->>D: 現在の組織に属する部署を識別子順に一覧取得する。
        A->>D: 現在の組織の利用者の部署所属を、所属部署・権限・有効状態を指定して登録する。
        A->>D: 現在の組織に属する部署所属を識別子順に一覧取得する。
        A->>D: 現在の組織に属する指定の部署所属について、所属部署・利用者・執筆や審査の権限・有効状態を更新する。
        A->>D: 組織の改訂番号が一致する場合だけ番号を進め、認可判定と権限失効の競合を検出する。
        A->>D: 現在の組織の組織名・改訂番号・利用停止状態を取得する。
        A->>D: 現在の組織に属する指定の利用者について、認証主体・表示名・有効状態・運用権限を取得する。
        A->>D: 現在の組織に属する利用者を識別子順に一覧取得する。
        A->>D: 必要な変更を確定（競合時rollback）
        A-->>U: 認可済み結果
    end
```

**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.Context.permission | 59 | For | For |
| kotorelay.context.Context.permission | 60 | If | m.department_id == department_id |
| kotorelay.context.Context.permission | 61 | Return | {'author': m.can_author, 'review': m.can_review, 'manage': m.leader, 'draft': m.can_author or m.can_review}.get(operation, False) |
| kotorelay.context.Context.permission | 67 | Return | False |
| kotorelay.context.new_id | 22 | Return | str(uuid4()) |
| kotorelay.context.now | 18 | Return | datetime.now(UTC) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.operations.groups.functions.change | 41 | If | rows |
| kotorelay.operations.groups.functions.change | 47 | Return | row |
| kotorelay.operations.groups.router.change_membership | 27 | Return | f.change(ctx, data) |
