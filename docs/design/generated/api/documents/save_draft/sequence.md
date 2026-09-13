<!-- 実装から生成。直接編集しない。入力SHA256: 1c655589065a087f66d0ae05a6e0b777b889337ba2d8cca7542a2988c7248164 -->

# 競合を検出して下書きを保存 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API router
    participant F as 個別処理 functions
    participant D as PostgreSQLまたはDSQL
    participant S as 内容ハッシュ実体
    participant M as モデル・検索エンジン
    U->>A: PUT /api/documents/{document_id}/draft
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
    A->>F: 現在の組織に属する下書きを識別子順に一覧取得する。
    A->>D: 現在の組織に属する下書きを識別子順に一覧取得する。
    A->>F: 下書きが読み込み時点から変更されていないことを確認する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: validate_placements
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    loop data.placements
    A->>D: 現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。
    A->>D: 現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    end
    A->>F: 本文または画像の実体を保存して内容ハッシュのキーを取得する。
    A->>S: 実体を保存
    A->>F: 現在の組織に属する指定の下書きについて、本文の保存先・画像配置・改訂番号を更新する。
    A->>D: 現在の組織に属する指定の下書きについて、本文の保存先・画像配置・改訂番号を更新する。
    A->>F: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。
    A->>F: now
    A->>D: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。
    A->>F: 組織の更新競合を検出するための書込みフェンスを更新する。
    A->>F: fence
    A->>D: 組織の改訂番号が一致する場合だけ番号を進め、認可判定と権限失効の競合を検出する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: 指定文書を取得して下書きの閲覧権限を確認する。
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
    A->>F: 組織内の下書きから対象文書の現在の改訂を取得する。
    A->>D: 現在の組織に属する下書きを識別子順に一覧取得する。
    A->>F: 下書き本文のハッシュを照合してテキストを復元する。
    A->>S: 実体を取得・ハッシュ照合
    A->>F: 文書・本文・改訂番号・画像配置を下書きの応答用データにまとめる。
    A->>F: 公開する応答型で業務結果を検証し、レスポンスの境界を保証する。
    Note over A: この処理からreturn
    Note over A,D: 成功応答前に依存transactionをcommit・失敗時rollback
    A-->>U: HTTP応答
```

**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.Context.document | 111 | Return | doc |
| kotorelay.context.now | 19 | Return | datetime.now(UTC) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.operations.documents.save_draft.functions.check_concurrent_access | 95 | Return | ctx.fence() |
| kotorelay.operations.documents.save_draft.functions.document_doc | 39 | Return | ctx.document(str(document_id), 'author') |
| kotorelay.operations.documents.save_draft.functions.documents_update | 82 | Return | q.documents_update(ctx.db, q.DocumentsUpdateParams.model_validate(doc.model_copy(update={'title': data.title, 'revision': doc.revision + 1, 'updated_at': now()}), from_attributes=True)) |
| kotorelay.operations.documents.save_draft.functions.drafts_list | 44 | Return | q.drafts_list(ctx.db, q.DraftsListParams(organization_id=ctx.org)) |
| kotorelay.operations.documents.save_draft.functions.drafts_update | 61 | Return | q.drafts_update(ctx.db, q.DraftsUpdateParams.model_validate(row.model_copy(update={'body_key': key, 'body_hash': key, 'revision': row.revision + 1, 'updated_by': ctx.user.id, 'placements': json.dumps([p.model_dump() for p in data.placements])}), from_attributes=True)) |
| kotorelay.operations.documents.save_draft.functions.put_key | 54 | Return | ctx.objects.put(data.body.encode(), 'text/markdown') |
| kotorelay.operations.documents.save_draft.functions.validate_draft_revision | 49 | Return | require(row.revision == data.revision, 'conflict', 409) |
| kotorelay.operations.documents.save_draft.functions.validate_placements | 19 | For | For |
| kotorelay.operations.documents.save_draft.response_builders.build_response | 10 | Return | TypeAdapter(ResponseData).validate_python(value) |
| kotorelay.operations.documents.save_draft.router.save_draft | 38 | Return | build_response(draft_functions.build_draft_data(current_document, current_draft, body)) |
| kotorelay.operations.documents.shared.functions.authorize_draft | 12 | Return | ctx.document(document_id, 'draft') |
| kotorelay.operations.documents.shared.functions.build_draft_data | 33 | Return | {'document': doc, 'body': body, 'revision': row.revision, 'placements': json.loads(row.placements)} |
| kotorelay.operations.documents.shared.functions.load_draft_body | 26 | Return | ctx.objects.get(row.body_key, row.body_hash).decode() |
| kotorelay.operations.documents.shared.functions.load_draft_row | 17 | Return | next((row for row in q.drafts_list(ctx.db, q.DraftsListParams(organization_id=ctx.org)) if row.document_id == document_id)) |
