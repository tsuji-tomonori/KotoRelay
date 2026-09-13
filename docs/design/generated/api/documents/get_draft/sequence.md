<!-- 実装から生成。直接編集しない。入力SHA256: 1c655589065a087f66d0ae05a6e0b777b889337ba2d8cca7542a2988c7248164 -->

# 下書きを取得 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API router
    participant F as 個別処理 functions
    participant D as PostgreSQLまたはDSQL
    participant S as 内容ハッシュ実体
    participant M as モデル・検索エンジン
    U->>A: GET /api/documents/{document_id}/draft
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
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.operations.documents.get_draft.response_builders.build_response | 10 | Return | TypeAdapter(ResponseData).validate_python(value) |
| kotorelay.operations.documents.get_draft.router.get_draft | 29 | Return | build_response(draft_functions.build_draft_data(current_document, current_draft, body)) |
| kotorelay.operations.documents.shared.functions.authorize_draft | 12 | Return | ctx.document(document_id, 'draft') |
| kotorelay.operations.documents.shared.functions.build_draft_data | 33 | Return | {'document': doc, 'body': body, 'revision': row.revision, 'placements': json.loads(row.placements)} |
| kotorelay.operations.documents.shared.functions.load_draft_body | 26 | Return | ctx.objects.get(row.body_key, row.body_hash).decode() |
| kotorelay.operations.documents.shared.functions.load_draft_row | 17 | Return | next((row for row in q.drafts_list(ctx.db, q.DraftsListParams(organization_id=ctx.org)) if row.document_id == document_id)) |
