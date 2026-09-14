<!-- 実装から生成。直接編集しない。入力SHA256: 0ce2ee5ffefd1f44a0c3da213ceff59dfb82649c9add5715e204664ffd05fd84 -->

# manifestを確認して承認・却下 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API router
    participant F as 個別処理 functions
    participant E as HTTP例外ハンドラ
    participant L as 型付き運用ログ
    participant D as PostgreSQLまたはDSQL
    participant S as 内容ハッシュ実体
    participant M as モデル・検索エンジン
    U->>A: POST /api/reviews/{submission_id}/decision
    Note over A,D: 依存注入でtransaction開始・組織と所属を確認
    A->>D: 現在の組織の組織名・改訂番号・利用停止状態を取得する。
    opt 検証不成立：bool(organizations) and (not organizations[0].suspended)
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 401 / {code： "unauthenticated", message： "ログインが必要です。", request_id： 相関ID}
    end
    end
    A->>D: 現在の組織に属する利用者を識別子順に一覧取得する。
    opt 検証不成立：len(users) == 1
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 401 / {code： "unauthenticated", message： "ログインが必要です。", request_id： 相関ID}
    end
    end
    A->>D: 現在の組織に属する部署を識別子順に一覧取得する。
    A->>D: 現在の組織に属する部署所属を識別子順に一覧取得する。
    A->>F: 現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を取得する。
    A->>D: 現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を取得する。
    A->>F: 対象の承認申請が存在することを確認する。
    opt 検証不成立：bool(rows)
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 404 / {code： "not_found", message： "対象を利用できません。", request_id： 相関ID}
    end
    end
    A->>F: 文書を取得して要求された操作の権限を確認する。
    A->>F: document
    A->>D: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。
    opt 検証不成立：bool(rows)
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 404 / {code： "not_found", message： "対象を利用できません。", request_id： 相関ID}
    end
    end
    opt 検証不成立：allowed
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 404 / {code： "not_found", message： "対象を利用できません。", request_id： 相関ID}
    end
    end
    A->>F: 要求内容の一致を確認して同じ冪等キーの記録済み結果を取得する。
    A->>F: idempotent_result
    A->>F: stable_id
    A->>D: 現在の組織に属する指定の再送判定の記録について、実行済み操作の入力ハッシュと応答を取得する。
    opt 前条件が成立
    A->>F: digest
    end
    opt 検証不成立：record.operation == operation and record.request_hash == digest(request.encode())
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 409 / {code： "idempotency_conflict", message： "同じ操作IDが異なる内容で使用されています。", request_id： 相関ID}
    end
    end
    alt cached
    A->>F: 後続処理に渡すデータを組み立てる。
    A->>F: 公開する応答型で業務結果を検証し、レスポンスの境界を保証する。
    Note over A: この処理からreturn
    end
    A->>F: 未決裁の申請であることを確認する。
    opt 検証不成立：submission.status == 'pending'
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 409 / {code： "conflict", message： "他の操作で更新されました。最新の状態を確認してください。", request_id： 相関ID}
    end
    end
    A->>F: 対象文書に属する確定版を取得する。
    A->>F: version
    A->>D: 現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。
    opt 検証不成立：bool(rows) and rows[0].document_id == doc.id
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 404 / {code： "not_found", message： "対象を利用できません。", request_id： 相関ID}
    end
    end
    alt not self.permission(doc.department_id, 'draft')
    opt 検証不成立：self.can_read(doc) and doc.latest_version_id == version.id
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 404 / {code： "not_found", message： "対象を利用できません。", request_id： 相関ID}
    end
    end
    end
    A->>F: digest
    opt 検証不成立：digest(version.manifest.encode()) == version.manifest_hash
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_FAILED / 処理を完了できずエラー応答を返しました。
    E-->>U: HTTP 503 / {code： "integrity", message： "保存内容の整合性を確認できません。", request_id： 相関ID}
    end
    end
    A->>F: 版の作成者による自己承認を拒否する。
    opt 検証不成立：version.created_by != ctx.user.id
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 403 / {code： "self_approval", message： "自分が作成した版は承認できません。", request_id： 相関ID}
    end
    end
    A->>F: 申請・確認画面・確定版のmanifestハッシュが一致することを確認する。
    opt 検証不成立：submission.manifest_hash == data.manifest_hash == version.manifest_hash
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 409 / {code： "conflict", message： "他の操作で更新されました。最新の状態を確認してください。", request_id： 相関ID}
    end
    end
    A->>F: 却下するときに理由が入力されていることを確認する。
    opt 検証不成立：data.decision != 'rejected' or bool(data.reason.strip())
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 422 / {code： "reason_required", message： "理由を入力してください。", request_id： 相関ID}
    end
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
    opt 検証不成立：q.organizations_fence(self.db, q.OrganizationsFenceParams.model_validate(self.organization, from_attributes=True)) == 1
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 409 / {code： "conflict", message： "他の操作で更新されました。最新の状態を確認してください。", request_id： 相関ID}
    end
    end
    A->>F: 公開する応答型で業務結果を検証し、レスポンスの境界を保証する。
    Note over A: この処理からreturn
    Note over A,D: 成功応答前に依存transactionをcommit・失敗時rollback
    A-->>U: HTTP 200 / models.SubmissionsRow
    Note over A,U: 共通例外経路（成功後に実行する追加処理ではない）
    opt 入力検証の失敗（RequestValidationError）
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 422 / {code： "invalid_input", message： "入力形式を確認してください。", request_id： 相関ID}
    end
    end
    opt SQL実行またはcommitの競合（psycopg.Error）
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 409 / {code： "conflict", message： "競合しました。再読込してください。", request_id： 相関ID}
    end
    end
    opt DB接続・外部サービスの失敗（捕捉して継続する場合を除く）
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_FAILED / 処理を完了できずエラー応答を返しました。
    E-->>U: HTTP 503 / {code： "unavailable", message： "一時的に利用できません。", request_id： 相関ID}
    end
    end
```

**例外応答一覧（HTTP境界へ到達した場合）**

| HTTP | code | message | 相関ID |
| --- | --- | --- | --- |
| 401 | unauthenticated | ログインが必要です。 | request_id |
| 403 | self_approval | 自分が作成した版は承認できません。 | request_id |
| 404 | not_found | 対象を利用できません。 | request_id |
| 409 | conflict | 他の操作で更新されました。最新の状態を確認してください。 | request_id |
| 409 | conflict | 競合しました。再読込してください。 | request_id |
| 409 | idempotency_conflict | 同じ操作IDが異なる内容で使用されています。 | request_id |
| 422 | invalid_input | 入力形式を確認してください。 | request_id |
| 422 | reason_required | 理由を入力してください。 | request_id |
| 503 | integrity | 保存内容の整合性を確認できません。 | request_id |
| 503 | unavailable | 一時的に利用できません。 | request_id |


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
