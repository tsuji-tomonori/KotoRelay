<!-- 実装から生成。直接編集しない。入力SHA256: 987c18a693c5fa5c9f59f732c65771f1c047c0829e22a5d72b689276aae93c56 -->

# manifestを確認して承認・却下 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API
    participant D as PostgreSQLまたはDSQL
    participant S as S3実体
    participant M as Bedrock
    U->>A: POST /api/reviews/{submission_id}/decision
    A->>D: 有効組織・所属を取得
    alt 認可条件が不成立
        A-->>U: 401または403または404
    else 許可
        A->>D: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。
        A->>D: 現在の組織の反映・削除ジョブを、対象文書と版・処理種別を指定して登録する。
        A->>D: 現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を取得する。
        A->>D: 現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を更新する。
        A->>D: 現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。
        A->>D: 現在の組織の監査記録として、操作した利用者・対象・変更前後の状態・理由を登録する。
        A->>D: 現在の組織に属する部署を識別子順に一覧取得する。
        A->>D: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。
        A->>D: 現在の組織に属する指定の再送判定の記録について、実行済み操作の入力ハッシュと応答を取得する。
        A->>D: 現在の組織の操作の再送を判定するため、実行済み操作の入力ハッシュと応答を登録する。
        A->>D: 現在の組織に属する部署所属を識別子順に一覧取得する。
        A->>D: 組織の改訂番号が一致する場合だけ番号を進め、認可判定と権限失効の競合を検出する。
        A->>D: 現在の組織の組織名・改訂番号・利用停止状態を取得する。
        A->>D: 現在の組織に属する利用者を識別子順に一覧取得する。
        A->>D: 現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。
        A->>S: 内容ハッシュ実体を照合
        opt 実体欠落・ハッシュ不一致
            A-->>U: 利用不可・回答保留
        end
        A->>D: 必要な変更を確定（競合時rollback）
        A-->>U: 認可済み結果
    end
```

**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.Context.document | 91 | Return | doc |
| kotorelay.context.Context.idempotent_result | 130 | If | not rows |
| kotorelay.context.Context.idempotent_result | 131 | Return | None |
| kotorelay.context.Context.idempotent_result | 138 | Return | record.response |
| kotorelay.context.Context.version | 97 | If | not self.permission(doc.department_id, 'draft') |
| kotorelay.context.Context.version | 101 | Return | version |
| kotorelay.context.new_id | 23 | Return | str(uuid4()) |
| kotorelay.context.now | 19 | Return | datetime.now(UTC) |
| kotorelay.context.stable_id | 27 | Return | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.objects.digest | 17 | Return | hashlib.sha256(data).hexdigest() |
| kotorelay.operations.reviews.decide_review.functions.decide | 19 | If | cached |
| kotorelay.operations.reviews.decide_review.functions.decide | 20 | Return | models.SubmissionsRow.model_validate_json(cached) |
| kotorelay.operations.reviews.decide_review.functions.decide | 37 | If | data.decision == 'approved' |
| kotorelay.operations.reviews.decide_review.functions.decide | 41 | If | not previous or previous[0].number < version.number |
| kotorelay.operations.reviews.decide_review.functions.decide | 69 | Return | updated |
| kotorelay.operations.reviews.decide_review.response_builders.build_response | 10 | Return | TypeAdapter(ResponseData).validate_python(value) |
| kotorelay.operations.reviews.decide_review.router.decide_review | 26 | Return | build_response(f.decide(ctx, str(submission_id), data, str(key))) |
