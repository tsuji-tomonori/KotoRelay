<!-- 実装から生成。直接編集しない。入力SHA256: 7ce322b2bb5c68dab4c51499ae55d5e49bae34d22b47e21dd6264975362b5d49 -->

# リーダーが公開範囲・公開停止・削除を管理 — シーケンス

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
    U->>A: PUT /api/documents/{document_id}/policy
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
    A->>F: 文書が読み込み時点から変更されていないことを確認する。
    opt 検証不成立：doc.revision == data.revision
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 409 / {code： "conflict", message： "他の操作で更新されました。最新の状態を確認してください。", request_id： 相関ID}
    end
    end
    A->>F: 文書を削除するときに理由が入力されていることを確認する。
    opt 検証不成立：data.status != 'deleted' or bool(data.reason.strip())
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 422 / {code： "reason_required", message： "理由を入力してください。", request_id： 相関ID}
    end
    end
    A->>F: 処理対象の識別子を重複なく取り出す。
    A->>D: 現在の組織に属する部署を識別子順に一覧取得する。
    A->>F: 共有先の全部署が現在の組織に存在することを確認する。
    opt 検証不成立：set(data.shared_departments) <= departments
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 422 / {code： "forbidden", message： "この操作は許可されていません。", request_id： 相関ID}
    end
    end
    A->>F: 後続処理に渡すデータを組み立てる。
    A->>F: now
    A->>F: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。
    A->>D: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。
    A->>F: 現在の組織の反映・削除ジョブを、対象文書と版・処理種別を指定して登録する。
    A->>F: new_id
    A->>F: now
    A->>D: 現在の組織の反映・削除ジョブを、対象文書と版・処理種別を指定して登録する。
    A->>F: 実行した変更の対象と結果を監査記録へ追加する。
    A->>F: audit
    A->>F: new_id
    A->>F: now
    A->>D: 現在の組織の監査記録として、操作した利用者・対象・変更前後の状態・理由を登録する。
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
    A-->>U: HTTP 200 / models.DocumentsRow
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
| 404 | not_found | 対象を利用できません。 | request_id |
| 409 | conflict | 他の操作で更新されました。最新の状態を確認してください。 | request_id |
| 409 | conflict | 競合しました。再読込してください。 | request_id |
| 422 | forbidden | この操作は許可されていません。 | request_id |
| 422 | invalid_input | 入力形式を確認してください。 | request_id |
| 422 | reason_required | 理由を入力してください。 | request_id |
| 503 | unavailable | 一時的に利用できません。 | request_id |


**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.Context.document | 111 | Return | doc |
| kotorelay.context.new_id | 23 | Return | str(uuid4()) |
| kotorelay.context.now | 19 | Return | datetime.now(UTC) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.operations.documents.change_policy.functions.build_updated | 51 | Return | doc.model_copy(update={'visibility': data.visibility, 'shared_departments': json.dumps(data.shared_departments), 'status': data.status, 'revision': doc.revision + 1, 'updated_at': now()}) |
| kotorelay.operations.documents.change_policy.functions.check_concurrent_access | 98 | Return | ctx.fence() |
| kotorelay.operations.documents.change_policy.functions.collect_departments | 35 | Return | {d.id for d in q.departments_list(ctx.db, q.DepartmentsListParams(organization_id=ctx.org)) if d.active} |
| kotorelay.operations.documents.change_policy.functions.document_doc | 18 | Return | ctx.document(str(document_id), 'manage') |
| kotorelay.operations.documents.change_policy.functions.documents_update | 64 | Return | q.documents_update(ctx.db, q.DocumentsUpdateParams.model_validate(updated, from_attributes=True)) |
| kotorelay.operations.documents.change_policy.functions.outbox_insert | 73 | Return | q.outbox_insert(ctx.db, q.OutboxInsertParams(id=new_id(), organization_id=ctx.org, document_id=doc.id, version_id=doc.latest_version_id, kind='purge' if data.status == 'deleted' else 'index', status='pending', attempts=0, error_code='', created_at=now())) |
| kotorelay.operations.documents.change_policy.functions.record_change_policy_audit | 93 | Return | ctx.audit('policy', doc.id, before=doc.status, after=data.status, reason=data.reason) |
| kotorelay.operations.documents.change_policy.functions.require_deletion_reason | 30 | Return | require(data.status != 'deleted' or bool(data.reason.strip()), 'reason_required', 422) |
| kotorelay.operations.documents.change_policy.functions.validate_document_revision | 25 | Return | require(doc.revision == data.revision, 'conflict', 409) |
| kotorelay.operations.documents.change_policy.functions.validate_shared_departments | 44 | Return | require(set(data.shared_departments) <= departments, 'forbidden', 422) |
| kotorelay.operations.documents.change_policy.response_builders.build_response | 10 | Return | TypeAdapter(ResponseData).validate_python(value) |
| kotorelay.operations.documents.change_policy.router.change_policy | 37 | Return | build_response(updated) |
