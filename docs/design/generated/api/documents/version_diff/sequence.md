<!-- 実装から生成。直接編集しない。入力SHA256: 1c655589065a087f66d0ae05a6e0b777b889337ba2d8cca7542a2988c7248164 -->

# 版IDを指定して本文差分を比較 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API router
    participant F as 個別処理 functions
    participant D as PostgreSQLまたはDSQL
    participant S as 内容ハッシュ実体
    participant M as モデル・検索エンジン
    U->>A: GET /api/documents/{document_id}/diff
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
    A->>F: 対象文書に属する確定版を取得する。
    A->>F: version
    A->>D: 現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    alt not self.permission(doc.department_id, 'draft')
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    end
    A->>F: digest
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: 対象文書に属する確定版を取得する。
    A->>F: version
    A->>D: 現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    alt not self.permission(doc.department_id, 'draft')
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    end
    A->>F: digest
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: 版の本文を比較用の行へ分割する。
    A->>S: 実体を取得・ハッシュ照合
    A->>F: 版の本文を比較用の行へ分割する。
    A->>S: 実体を取得・ハッシュ照合
    A->>F: 二つの版の本文から統一差分形式の変更行を生成する。
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
| kotorelay.context.Context.version | 117 | If | not self.permission(doc.department_id, 'draft') |
| kotorelay.context.Context.version | 121 | Return | version |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.objects.digest | 17 | Return | hashlib.sha256(data).hexdigest() |
| kotorelay.operations.documents.version_diff.functions.build_version_diff | 43 | Return | {'left': str(left), 'right': str(right), 'diff': '\n'.join(lines)} |
| kotorelay.operations.documents.version_diff.functions.compare_bodies | 50 | Return | list(difflib.unified_diff(left_lines, right_lines, fromfile=left, tofile=right, lineterm='')) |
| kotorelay.operations.documents.version_diff.functions.document_doc | 14 | Return | ctx.document(str(document_id), 'draft') |
| kotorelay.operations.documents.version_diff.functions.load_left_lines | 33 | Return | ctx.objects.get(a.body_key).decode().splitlines() |
| kotorelay.operations.documents.version_diff.functions.load_left_version | 21 | Return | ctx.version(doc, str(left)) |
| kotorelay.operations.documents.version_diff.functions.load_right_lines | 38 | Return | ctx.objects.get(b.body_key).decode().splitlines() |
| kotorelay.operations.documents.version_diff.functions.load_right_version | 28 | Return | ctx.version(doc, str(right)) |
| kotorelay.operations.documents.version_diff.response_builders.build_response | 10 | Return | TypeAdapter(ResponseData).validate_python(value) |
| kotorelay.operations.documents.version_diff.router.version_diff | 33 | Return | build_response(f.build_version_diff(left, right, lines)) |
