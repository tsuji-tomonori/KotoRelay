<!-- 実装から生成。直接編集しない。入力SHA256: 1c655589065a087f66d0ae05a6e0b777b889337ba2d8cca7542a2988c7248164 -->

# 正本と索引の不一致を確認 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API router
    participant F as 個別処理 functions
    participant D as PostgreSQLまたはDSQL
    participant S as 内容ハッシュ実体
    participant M as モデル・検索エンジン
    U->>A: GET /api/operations/reconcile
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
    A->>F: 索引整合を確認できる運用権限を確認する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: 現在の組織に属する検索用の文書断片を識別子順に一覧取得する。
    A->>D: 現在の組織に属する検索用の文書断片を識別子順に一覧取得する。
    A->>F: 現在の組織に属する文書を識別子順に一覧取得する。
    A->>D: 現在の組織に属する文書を識別子順に一覧取得する。
    loop f.documents_list(ctx)
    A->>F: 用途と対象に一致するデータだけを取り出す。
    A->>F: 公開版が変わったか文書が失効したため不要になった断片があるかを判定する。
    alt f.has_outdated_chunks(current, doc)
    A->>F: 後続処理に渡すデータを組み立てる。
    end
    A->>F: 有効な公開版に反映済みの断片が存在しないかを判定する。
    alt f.needs_index_repair(doc, current)
    A->>F: 後続処理に渡すデータを組み立てる。
    end
    end
    A->>F: 公開する応答型で業務結果を検証し、レスポンスの境界を保証する。
    Note over A: この処理からreturn
    Note over A,D: 成功応答前に依存transactionをcommit・失敗時rollback
    A-->>U: HTTP応答
```

**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.operations.indexing.reconcile_index.functions.build_reconcile_index | 32 | Return | {'document_id': doc.id, 'reason': '旧版または停止済みの断片が残留'} |
| kotorelay.operations.indexing.reconcile_index.functions.build_reconcile_index_2 | 46 | Return | {'document_id': doc.id, 'reason': '最新承認版が未反映'} |
| kotorelay.operations.indexing.reconcile_index.functions.chunks_list | 17 | Return | q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org)) |
| kotorelay.operations.indexing.reconcile_index.functions.documents_list | 22 | Return | q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org)) |
| kotorelay.operations.indexing.reconcile_index.functions.has_outdated_chunks | 51 | Return | any((chunk.version_id != doc.latest_version_id or doc.status != 'active' for chunk in current)) |
| kotorelay.operations.indexing.reconcile_index.functions.needs_index_repair | 37 | Return | bool(doc.status == 'active' and doc.latest_version_id and (not any((c.version_id == doc.latest_version_id and c.ready for c in current)))) |
| kotorelay.operations.indexing.reconcile_index.functions.require_operator | 12 | Return | require(ctx.user.operator, 'forbidden', 403) |
| kotorelay.operations.indexing.reconcile_index.functions.select_current | 27 | Return | [c for c in chunks if c.document_id == doc.id] |
| kotorelay.operations.indexing.reconcile_index.response_builders.build_response | 10 | Return | TypeAdapter(ResponseData).validate_python(value) |
| kotorelay.operations.indexing.reconcile_index.router.reconcile_index | 26 | For | For |
| kotorelay.operations.indexing.reconcile_index.router.reconcile_index | 28 | If | f.has_outdated_chunks(current, doc) |
| kotorelay.operations.indexing.reconcile_index.router.reconcile_index | 30 | If | f.needs_index_repair(doc, current) |
| kotorelay.operations.indexing.reconcile_index.router.reconcile_index | 32 | Return | build_response(differences) |
