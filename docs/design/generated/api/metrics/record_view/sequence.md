<!-- 実装から生成。直接編集しない。入力SHA256: 1c655589065a087f66d0ae05a6e0b777b889337ba2d8cca7542a2988c7248164 -->

# 実閲覧を一意IDで記録 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API router
    participant F as 個別処理 functions
    participant D as PostgreSQLまたはDSQL
    participant S as 内容ハッシュ実体
    participant M as モデル・検索エンジン
    U->>A: POST /api/metrics/views/{document_id}
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
    A->>F: 文書を取得して要求された操作の権限を確認する。
    A->>F: document
    A->>D: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: 閲覧対象に公開中の承認版が存在することを確認する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: 閲覧の帰属先部署への所属を確認する。
    A->>F: member
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: stable_id
    A->>F: 現在の組織に属する指定の利用イベントについて、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を取得する。
    A->>D: 現在の組織に属する指定の利用イベントについて、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を取得する。
    alt previous
    A->>F: 同じ冪等キーの閲覧対象と帰属部署が一致することを確認する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: 後続処理に渡すデータを組み立てる。
    A->>F: 公開する応答型で業務結果を検証し、レスポンスの境界を保証する。
    Note over A: この処理からreturn
    end
    A->>F: 現在の組織の利用イベントとして、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を登録する。
    A->>F: now
    A->>D: 現在の組織の利用イベントとして、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を登録する。
    A->>F: 組織の更新競合を検出するための書込みフェンスを更新する。
    A->>F: fence
    A->>D: 組織の改訂番号が一致する場合だけ番号を進め、認可判定と権限失効の競合を検出する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: 後続処理に渡すデータを組み立てる。
    A->>F: 公開する応答型で業務結果を検証し、レスポンスの境界を保証する。
    Note over A: この処理からreturn
    Note over A,D: 成功応答前に依存transactionをcommit・失敗時rollback
    A-->>U: HTTP応答
```

**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.Context.document | 111 | Return | doc |
| kotorelay.context.Context.member | 75 | Return | any((m.department_id == department_id for m in self.memberships)) |
| kotorelay.context.now | 19 | Return | datetime.now(UTC) |
| kotorelay.context.stable_id | 27 | Return | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.operations.metrics.record_view.functions.build_record_view | 52 | Return | {'recorded': False} |
| kotorelay.operations.metrics.record_view.functions.build_record_view_2 | 85 | Return | {'recorded': True} |
| kotorelay.operations.metrics.record_view.functions.check_concurrent_access | 80 | Return | ctx.fence() |
| kotorelay.operations.metrics.record_view.functions.document_doc | 17 | Return | ctx.document(str(document_id)) |
| kotorelay.operations.metrics.record_view.functions.events_get | 34 | Return | q.events_get(ctx.db, q.EventsGetParams(organization_id=ctx.org, id=event_id)) |
| kotorelay.operations.metrics.record_view.functions.events_insert | 62 | Return | q.events_insert(ctx.db, q.EventsInsertParams(id=event_id, organization_id=ctx.org, user_id=ctx.user.id, department_id=data.department_id, document_id=doc.id, answer_id=None, kind='view', outcome='viewed', created_at=now())) |
| kotorelay.operations.metrics.record_view.functions.require_consuming_membership | 29 | Return | require(ctx.member(data.department_id), 'forbidden', 403) |
| kotorelay.operations.metrics.record_view.functions.require_published_version | 22 | Return | require(bool(doc.latest_version_id)) |
| kotorelay.operations.metrics.record_view.functions.validate_repeated_view | 41 | Return | require(previous[0].document_id == doc.id and previous[0].department_id == data.department_id and (previous[0].kind == 'view'), 'idempotency_conflict', 409) |
| kotorelay.operations.metrics.record_view.response_builders.build_response | 10 | Return | TypeAdapter(ResponseData).validate_python(value) |
| kotorelay.operations.metrics.record_view.router.record_view | 32 | If | previous |
| kotorelay.operations.metrics.record_view.router.record_view | 34 | Return | build_response(f.build_record_view()) |
| kotorelay.operations.metrics.record_view.router.record_view | 37 | Return | build_response(f.build_record_view_2()) |
