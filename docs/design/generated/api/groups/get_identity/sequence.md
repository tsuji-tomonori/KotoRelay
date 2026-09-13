<!-- 実装から生成。直接編集しない。入力SHA256: 1c655589065a087f66d0ae05a6e0b777b889337ba2d8cca7542a2988c7248164 -->

# 本人と現在の所属権限を取得 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API router
    participant F as 個別処理 functions
    participant D as PostgreSQLまたはDSQL
    participant S as 内容ハッシュ実体
    participant M as モデル・検索エンジン
    U->>A: GET /api/groups/me
    Note over A,D: 依存注入でtransaction開始・組織と所属を確認
    A->>D: 現在の組織の組織名・改訂番号・利用停止状態を取得する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>D: 現在の組織に属する利用者を識別子順に一覧取得する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>D: 現在の組織に属する部署を識別子順に一覧取得する。
    A->>D: 現在の組織に属する部署所属を識別子順に一覧取得する。
    A->>F: 後続処理に渡すデータを組み立てる。
    A->>D: 現在の組織に属する部署を識別子順に一覧取得する。
    loop q.departments_list(ctx.db, q.DepartmentsListParams(organization_id=ctx.org))
    A->>F: member
    end
    A->>D: 現在の組織に属する部署を識別子順に一覧取得する。
    A->>F: 公開する応答型で業務結果を検証し、レスポンスの境界を保証する。
    Note over A: この処理からreturn
    Note over A,D: 成功応答前に依存transactionをcommit・失敗時rollback
    A-->>U: HTTP応答
```

**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.Context.member | 75 | Return | any((m.department_id == department_id for m in self.memberships)) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.operations.groups.get_identity.functions.build_get_identity | 11 | Return | {'user': ctx.user, 'memberships': ctx.memberships, 'departments': [d for d in q.departments_list(ctx.db, q.DepartmentsListParams(organization_id=ctx.org)) if ctx.member(d.id)], 'directory': [d for d in q.departments_list(ctx.db, q.DepartmentsListParams(organization_id=ctx.org)) if d.active], 'mode': ctx.settings.mode} |
| kotorelay.operations.groups.get_identity.response_builders.build_response | 10 | Return | TypeAdapter(ResponseData).validate_python(value) |
| kotorelay.operations.groups.get_identity.router.get_identity | 23 | Return | build_response(f.build_get_identity(ctx)) |
