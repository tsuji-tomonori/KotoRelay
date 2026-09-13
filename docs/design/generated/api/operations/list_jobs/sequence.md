<!-- 実装から生成。直接編集しない。入力SHA256: 1c655589065a087f66d0ae05a6e0b777b889337ba2d8cca7542a2988c7248164 -->

# 反映ジョブと失敗理由を確認 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API router
    participant F as 個別処理 functions
    participant D as PostgreSQLまたはDSQL
    participant S as 内容ハッシュ実体
    participant M as モデル・検索エンジン
    U->>A: GET /api/operations/jobs
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
    alt details
    A->>F: 索引ジョブを閲覧できる運用権限を確認する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: 現在の組織に属する反映・削除ジョブを識別子順に一覧取得する。
    A->>D: 現在の組織に属する反映・削除ジョブを識別子順に一覧取得する。
    Note over A: この処理からreturn
    A->>F: 取得したデータを識別子別に参照できる辞書へ変換する。
    A->>D: 現在の組織に属する文書を識別子順に一覧取得する。
    A->>F: 取得したデータを識別子別に参照できる辞書へ変換する。
    A->>D: 現在の組織に属する文書版を識別子順に一覧取得する。
    A->>F: 用途と対象に一致するデータだけを取り出す。
    Note over A: この処理からreturn
    A->>F: 公開する応答型で業務結果を検証し、レスポンスの境界を保証する。
    Note over A: この処理からreturn
    end
    A->>F: 索引ジョブを閲覧できる運用権限を確認する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: 現在の組織に属する反映・削除ジョブを識別子順に一覧取得する。
    A->>D: 現在の組織に属する反映・削除ジョブを識別子順に一覧取得する。
    Note over A: この処理からreturn
    A->>F: 用途と対象に一致するデータだけを取り出す。
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
| kotorelay.operations.indexing.list_jobs.functions.map_docs | 28 | Return | {d.id: d for d in q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org))} |
| kotorelay.operations.indexing.list_jobs.functions.map_versions | 35 | Return | {v.id: v for v in q.versions_list(ctx.db, q.VersionsListParams(organization_id=ctx.org))} |
| kotorelay.operations.indexing.list_jobs.functions.outbox_list | 23 | Return | q.outbox_list(ctx.db, q.OutboxListParams(organization_id=ctx.org)) |
| kotorelay.operations.indexing.list_jobs.functions.require_operator | 18 | Return | require(ctx.user.operator, 'forbidden', 403) |
| kotorelay.operations.indexing.list_jobs.functions.select_job_details | 44 | Return | [dict(row.model_dump(), title=docs[row.document_id].title, version_number=versions[row.version_id].number if row.version_id else None) for row in rows] |
| kotorelay.operations.indexing.list_jobs.functions.select_list_jobs | 13 | Return | [row.model_dump() for row in rows] |
| kotorelay.operations.indexing.list_jobs.response_builders.build_response | 10 | Return | TypeAdapter(ResponseData).validate_python(value) |
| kotorelay.operations.indexing.list_jobs.router.job_details | 40 | Return | f.select_job_details(rows, docs, versions) |
| kotorelay.operations.indexing.list_jobs.router.jobs | 33 | Return | list(f.outbox_list(ctx)) |
| kotorelay.operations.indexing.list_jobs.router.list_jobs | 26 | If | details |
| kotorelay.operations.indexing.list_jobs.router.list_jobs | 27 | Return | build_response(job_details(ctx)) |
| kotorelay.operations.indexing.list_jobs.router.list_jobs | 28 | Return | build_response(f.select_list_jobs(jobs(ctx))) |
