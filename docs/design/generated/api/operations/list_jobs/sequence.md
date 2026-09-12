<!-- 実装から生成。直接編集しない。入力SHA256: 4c18ae62a9b9de513581947abfc60f1ec45b9f631019a142a812724b4695a84b -->

# 反映ジョブと失敗理由を確認 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API
    participant D as PostgreSQLまたはDSQL
    participant S as S3実体
    participant M as Bedrock
    U->>A: GET /api/operations/jobs
    A->>D: 有効組織・所属を取得
    alt 認可条件が不成立
        A-->>U: 401または403または404
    else 許可
        A->>D: departments_list
        A->>D: documents_list
        A->>D: memberships_list
        A->>D: organizations_get
        A->>D: outbox_list
        A->>D: users_list
        A->>D: versions_list
        A->>S: 内容ハッシュ実体を照合
        opt 実体欠落・ハッシュ不一致
            A-->>U: 利用不可・回答保留
        end
        opt 有効根拠または索引配送
            A->>M: 上限付きモデル実行
            alt 外部サービス失敗
                M-->>A: 例外
                A->>D: 失敗状態を記録
            else 成功
                M-->>A: 結果
            end
        end
        A->>D: 必要な変更を確定（競合時rollback）
        A-->>U: 認可済み結果
    end
```

**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.operations.indexing.functions.job_details | 207 | Return | [dict(row.model_dump(), title=docs[row.document_id].title, version_number=versions[row.version_id].number if row.version_id else None) for row in rows] |
| kotorelay.operations.indexing.functions.jobs | 200 | Return | q.outbox_list(ctx.db, ctx.org) |
| kotorelay.operations.indexing.router.list_jobs | 16 | Return | f.job_details(ctx) if details else [row.model_dump() for row in f.jobs(ctx)] |
