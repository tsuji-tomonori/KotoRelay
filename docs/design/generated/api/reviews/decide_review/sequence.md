<!-- 実装から生成。直接編集しない。入力SHA256: 1c655589065a087f66d0ae05a6e0b777b889337ba2d8cca7542a2988c7248164 -->

# manifestを確認して承認・却下 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API router
    participant F as 個別処理 functions
    participant D as PostgreSQLまたはDSQL
    participant S as 内容ハッシュ実体
    participant M as モデル・検索エンジン
    U->>A: POST /api/reviews/{submission_id}/decision
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
    A->>F: 現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を取得する。
    A->>D: 現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を取得する。
    A->>F: 対象の承認申請が存在することを確認する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
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
    A->>F: 要求内容の一致を確認して同じ冪等キーの記録済み結果を取得する。
    A->>F: idempotent_result
    A->>F: stable_id
    A->>D: 現在の組織に属する指定の再送判定の記録について、実行済み操作の入力ハッシュと応答を取得する。
    opt 前条件が成立
    A->>F: digest
    end
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    alt cached
    A->>F: 後続処理に渡すデータを組み立てる。
    A->>F: 公開する応答型で業務結果を検証し、レスポンスの境界を保証する。
    Note over A: この処理からreturn
    end
    A->>F: 未決裁の申請であることを確認する。
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
    A->>F: 版の作成者による自己承認を拒否する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: 申請・確認画面・確定版のmanifestハッシュが一致することを確認する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: 却下するときに理由が入力されていることを確認する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: 後続処理に渡すデータを組み立てる。
    A->>F: now
    A->>F: 現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を更新する。
    A->>D: 現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を更新する。
    A->>F: 申請を承認する決裁かを判定する。
    alt f.is_approved(data)
    alt doc.latest_version_id
    A->>F: 現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。
    A->>D: 現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。
    else 条件不成立
    end
    A->>F: 今回の版が公開中の版より新しいかを判定する。
    alt f.is_newer_publication(previous, version)
    A->>F: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。
    A->>F: now
    A->>D: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。
    A->>F: 現在の組織の反映・削除ジョブを、対象文書と版・処理種別を指定して登録する。
    A->>F: new_id
    A->>F: now
    A->>D: 現在の組織の反映・削除ジョブを、対象文書と版・処理種別を指定して登録する。
    end
    end
    A->>F: 実行した変更の対象と結果を監査記録へ追加する。
    A->>F: audit
    A->>F: new_id
    A->>F: now
    A->>D: 現在の組織の監査記録として、操作した利用者・対象・変更前後の状態・理由を登録する。
    A->>F: 同じ要求を安全に再試行できるよう冪等キーと結果を記録する。
    A->>F: remember
    A->>F: stable_id
    A->>F: digest
    A->>D: 現在の組織の操作の再送を判定するため、実行済み操作の入力ハッシュと応答を登録する。
    A->>F: 組織の更新競合を検出するための書込みフェンスを更新する。
    A->>F: fence
    A->>D: 組織の改訂番号が一致する場合だけ番号を進め、認可判定と権限失効の競合を検出する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: 公開する応答型で業務結果を検証し、レスポンスの境界を保証する。
    Note over A: この処理からreturn
    Note over A,D: 成功応答前に依存transactionをcommit・失敗時rollback
    A-->>U: HTTP応答
```

**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.Context.document | 111 | Return | doc |
| kotorelay.context.Context.idempotent_result | 153 | If | not rows |
| kotorelay.context.Context.idempotent_result | 154 | Return | None |
| kotorelay.context.Context.idempotent_result | 161 | Return | record.response |
| kotorelay.context.Context.version | 117 | If | not self.permission(doc.department_id, 'draft') |
| kotorelay.context.Context.version | 121 | Return | version |
| kotorelay.context.new_id | 23 | Return | str(uuid4()) |
| kotorelay.context.now | 19 | Return | datetime.now(UTC) |
| kotorelay.context.stable_id | 27 | Return | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.objects.digest | 17 | Return | hashlib.sha256(data).hexdigest() |
| kotorelay.operations.reviews.decide_review.functions.build_decide_review | 43 | Return | models.SubmissionsRow.model_validate_json(cached) |
| kotorelay.operations.reviews.decide_review.functions.build_updated | 81 | Return | submission.model_copy(update={'status': data.decision, 'reason': data.reason, 'decided_by': ctx.user.id, 'decided_at': now()}) |
| kotorelay.operations.reviews.decide_review.functions.check_concurrent_access | 173 | Return | ctx.fence() |
| kotorelay.operations.reviews.decide_review.functions.document_doc | 33 | Return | ctx.document(submission.document_id, 'review') |
| kotorelay.operations.reviews.decide_review.functions.documents_update | 117 | Return | q.documents_update(ctx.db, q.DocumentsUpdateParams.model_validate(doc.model_copy(update={'latest_version_id': version.id, 'revision': doc.revision + 1, 'updated_at': now()}), from_attributes=True)) |
| kotorelay.operations.reviews.decide_review.functions.find_previous_result | 38 | Return | ctx.idempotent_result(str(key), 'decide', request) |
| kotorelay.operations.reviews.decide_review.functions.is_approved | 100 | Return | bool(data.decision == 'approved') |
| kotorelay.operations.reviews.decide_review.functions.is_newer_publication | 110 | Return | bool(not previous or previous[0].number < version.number) |
| kotorelay.operations.reviews.decide_review.functions.outbox_insert | 136 | Return | q.outbox_insert(ctx.db, q.OutboxInsertParams(id=new_id(), organization_id=ctx.org, document_id=doc.id, version_id=version.id, kind='index', status='pending', attempts=0, error_code='', created_at=now())) |
| kotorelay.operations.reviews.decide_review.functions.prevent_self_approval | 60 | Return | require(version.created_by != ctx.user.id, 'self_approval', 403) |
| kotorelay.operations.reviews.decide_review.functions.record_decide_review_audit | 161 | Return | ctx.audit('review', doc.id, version.id, submission.status, updated.status, data.reason) |
| kotorelay.operations.reviews.decide_review.functions.remember_decide_review_result | 168 | Return | ctx.remember(str(key), 'decide', request, updated.model_dump_json()) |
| kotorelay.operations.reviews.decide_review.functions.require_pending_submission | 48 | Return | require(submission.status == 'pending', 'conflict', 409) |
| kotorelay.operations.reviews.decide_review.functions.require_rejection_reason | 74 | Return | require(data.decision != 'rejected' or bool(data.reason.strip()), 'reason_required', 422) |
| kotorelay.operations.reviews.decide_review.functions.require_submission | 26 | Return | require(bool(rows)) |
| kotorelay.operations.reviews.decide_review.functions.submissions_get | 19 | Return | q.submissions_get(ctx.db, q.SubmissionsGetParams(organization_id=ctx.org, id=str(submission_id))) |
| kotorelay.operations.reviews.decide_review.functions.submissions_update | 93 | Return | q.submissions_update(ctx.db, q.SubmissionsUpdateParams.model_validate(updated, from_attributes=True)) |
| kotorelay.operations.reviews.decide_review.functions.validate_manifest_hash | 67 | Return | require(submission.manifest_hash == data.manifest_hash == version.manifest_hash, 'conflict', 409) |
| kotorelay.operations.reviews.decide_review.functions.version_version | 55 | Return | ctx.version(doc, submission.version_id) |
| kotorelay.operations.reviews.decide_review.functions.versions_get | 105 | Return | q.versions_get(ctx.db, q.VersionsGetParams(organization_id=ctx.org, id=version_id)) |
| kotorelay.operations.reviews.decide_review.response_builders.build_response | 10 | Return | TypeAdapter(ResponseData).validate_python(value) |
| kotorelay.operations.reviews.decide_review.router.decide_review | 34 | If | cached |
| kotorelay.operations.reviews.decide_review.router.decide_review | 35 | Return | build_response(f.build_decide_review(cached)) |
| kotorelay.operations.reviews.decide_review.router.decide_review | 43 | If | f.is_approved(data) |
| kotorelay.operations.reviews.decide_review.router.decide_review | 45 | If | f.is_newer_publication(previous, version) |
| kotorelay.operations.reviews.decide_review.router.decide_review | 51 | Return | build_response(updated) |
