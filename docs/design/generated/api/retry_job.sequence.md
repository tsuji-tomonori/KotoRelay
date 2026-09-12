<!-- 実装から生成。直接編集しない。入力SHA256: e3cb305ddf380bd9917bab7f5404c8ac54c8511b8d91b58e7192aa0d5991c3cf -->

# 反映ジョブを再処理 — sequence

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API
    participant D as PostgreSQLまたはDSQL
    participant S as S3実体
    participant M as Bedrock
    U->>A: POST /api/operations/jobs/{job_id}
    A->>D: 有効組織・所属を取得
    alt 認可条件が不成立
        A-->>U: 401または403または404
    else 許可
        A->>D: answers_list
        A->>D: assets_delete
        A->>D: assets_get
        A->>D: assets_list
        A->>D: chunks_delete
        A->>D: chunks_insert
        A->>D: chunks_list
        A->>D: chunks_update
        A->>D: departments_list
        A->>D: documents_get
        A->>D: documents_list
        A->>D: drafts_delete
        A->>D: drafts_list
        A->>D: memberships_list
        A->>D: ocr_runs_delete
        A->>D: ocr_runs_get
        A->>D: ocr_runs_list
        A->>D: organizations_fence
        A->>D: organizations_get
        A->>D: outbox_get
        A->>D: outbox_update
        A->>D: users_list
        A->>D: versions_get
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

## 制御順序（関数内の行順）

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.now | 18 | Return | datetime.now(UTC) |
| kotorelay.context.stable_id | 26 | Return | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.operations.indexing.functions.build_index | 40 | If | doc.latest_version_id != job.version_id or not job.version_id |
| kotorelay.operations.indexing.functions.build_index | 41 | Return | 'obsolete' |
| kotorelay.operations.indexing.functions.build_index | 48 | For | For |
| kotorelay.operations.indexing.functions.build_index | 50 | If | len(stale) > 100 |
| kotorelay.operations.indexing.functions.build_index | 51 | Return | 'pending' |
| kotorelay.operations.indexing.functions.build_index | 52 | If | doc.status != 'active' |
| kotorelay.operations.indexing.functions.build_index | 53 | Return | 'done' |
| kotorelay.operations.indexing.functions.build_index | 60 | For | For |
| kotorelay.operations.indexing.functions.build_index | 66 | For | For |
| kotorelay.operations.indexing.functions.build_index | 72 | For | For |
| kotorelay.operations.indexing.functions.build_index | 87 | If | chunk.id in previous |
| kotorelay.operations.indexing.functions.build_index | 93 | For | For |
| kotorelay.operations.indexing.functions.build_index | 96 | Return | 'done' |
| kotorelay.operations.indexing.functions.process | 170 | If | job.status in {'done', 'obsolete'} |
| kotorelay.operations.indexing.functions.process | 171 | Return | job |
| kotorelay.operations.indexing.functions.process | 172 | Try | Try |
| kotorelay.operations.indexing.functions.process | 181 | ExceptHandler | Problem |
| kotorelay.operations.indexing.functions.process | 185 | ExceptHandler | (OSError, BotoCoreError, ClientError) |
| kotorelay.operations.indexing.functions.process | 195 | Return | updated |
| kotorelay.operations.indexing.functions.purge | 101 | If | doc.status != 'deleted' |
| kotorelay.operations.indexing.functions.purge | 102 | Return | 'obsolete' |
| kotorelay.operations.indexing.functions.purge | 103 | If | (now() - job.created_at).total_seconds() < ctx.settings.retention_days * 86400 |
| kotorelay.operations.indexing.functions.purge | 104 | Return | 'retained' |
| kotorelay.operations.indexing.functions.purge | 130 | For | For |
| kotorelay.operations.indexing.functions.purge | 131 | For | For |
| kotorelay.operations.indexing.functions.purge | 132 | If | row.document_id == doc.id |
| kotorelay.operations.indexing.functions.purge | 134 | If | row.document_id in live |
| kotorelay.operations.indexing.functions.purge | 136 | For | For |
| kotorelay.operations.indexing.functions.purge | 142 | For | For |
| kotorelay.operations.indexing.functions.purge | 146 | For | For |
| kotorelay.operations.indexing.functions.purge | 148 | If | len(target_chunks) > 100 |
| kotorelay.operations.indexing.functions.purge | 149 | Return | 'pending' |
| kotorelay.operations.indexing.functions.purge | 151 | For | For |
| kotorelay.operations.indexing.functions.purge | 153 | If | len(target_runs) > 100 |
| kotorelay.operations.indexing.functions.purge | 154 | Return | 'pending' |
| kotorelay.operations.indexing.functions.purge | 155 | For | For |
| kotorelay.operations.indexing.functions.purge | 156 | If | asset.document_id == doc.id |
| kotorelay.operations.indexing.functions.purge | 158 | For | For |
| kotorelay.operations.indexing.functions.purge | 159 | If | draft.document_id == doc.id |
| kotorelay.operations.indexing.functions.purge | 161 | Return | 'done' |
| kotorelay.operations.indexing.functions.split_chunks | 20 | For | For |
| kotorelay.operations.indexing.functions.split_chunks | 21 | If | line.startswith('#') or len(buffer) + len(line) > 1200 |
| kotorelay.operations.indexing.functions.split_chunks | 22 | If | buffer.strip() |
| kotorelay.operations.indexing.functions.split_chunks | 25 | If | line.startswith('#') |
| kotorelay.operations.indexing.functions.split_chunks | 27 | For | For |
| kotorelay.operations.indexing.functions.split_chunks | 29 | If | len(buffer) + len(part) > 1200 and buffer.strip() |
| kotorelay.operations.indexing.functions.split_chunks | 33 | If | buffer.strip() |
| kotorelay.operations.indexing.functions.split_chunks | 35 | Return | chunks |
| kotorelay.operations.indexing.router.retry_job | 21 | Return | f.process(ctx, rt.engine, str(job_id)) |
