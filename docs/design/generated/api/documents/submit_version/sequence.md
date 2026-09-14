<!-- 実装から生成。直接編集しない。入力SHA256: dc958b6e6841a9f29856eb932e8271e37a6d4416a3266624301c411c89949f81 -->

# 版を確定して承認申請 — シーケンス

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
    U->>A: POST /api/documents/{document_id}/submissions
    Note over A,D: 依存注入でtransaction開始・組織と所属を確認
    A->>D: 現在の組織の組織名・改訂番号・利用停止状態を取得する。
    opt 検証不成立：有効な組織と利用者を確認し、最新の所属を読み込む。
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 401 / ログインが必要です。
    end
    end
    A->>D: 現在の組織に属する利用者を識別子順に一覧取得する。
    opt 検証不成立：有効な組織と利用者を確認し、最新の所属を読み込む。
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 401 / ログインが必要です。
    end
    end
    A->>D: 現在の組織に属する部署を識別子順に一覧取得する。
    A->>D: 現在の組織に属する部署所属を識別子順に一覧取得する。
    A->>F: 文書を取得して要求された操作の権限を確認する。
    A->>F: 対象の文書が存在し、要求された操作を実行できることを確認する。
    A->>D: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。
    opt 検証不成立：対象の文書が存在し、要求された操作を実行できることを確認する。
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 404 / 対象を利用できません。
    end
    end
    A->>F: 文書の閲覧権限を確認する操作である。
    alt 文書の閲覧権限を確認する操作である。
    A->>F: 現在の所属と公開範囲で文書を閲覧できる。
    A->>F: 指定した部署に現在も所属している。
    opt 前条件が成立
    loop json.loads(doc.shared_departments)
    A->>F: 指定した部署に現在も所属している。
    end
    end
    else 条件不成立
    opt 前条件が成立
    A->>F: 指定した部署で要求された操作を実行できる。
    end
    end
    opt 検証不成立：対象の文書が存在し、要求された操作を実行できることを確認する。
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 404 / 対象を利用できません。
    end
    end
    A->>F: 要求内容の一致を確認して同じ冪等キーの記録済み結果を取得する。
    A->>F: 同じ冪等キーの処理内容が一致することを確認して保存済み応答を返す。
    A->>F: stable_id
    A->>D: 現在の組織に属する指定の再送判定の記録について、実行済み操作の入力ハッシュと応答を取得する。
    opt 前条件が成立
    A->>F: digest
    end
    opt 検証不成立：同じ冪等キーの処理内容が一致することを確認して保存済み応答を返す。
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 409 / 同じ操作IDが異なる内容で使用されています。
    end
    end
    A->>F: 同じ操作IDの処理結果が保存されている。
    alt 同じ操作IDの処理結果が保存されている。
    A->>F: 後続処理に渡すデータを組み立てる。
    A->>F: 公開する応答型で業務結果を検証し、レスポンスの境界を保証する。
    break 応答を返して終了
    Note over A,D: 成功応答前にtransactionをcommit・競合時rollback
    A-->>U: HTTP 201 / models.VersionsRow
    end
    end
    A->>F: 現在の組織に属する下書きを識別子順に一覧取得する。
    A->>D: 現在の組織に属する下書きを識別子順に一覧取得する。
    loop f.drafts_list(ctx)
    A->>F: 下書きが申請対象の文書に属する。
    end
    A->>F: 申請元の下書きが読み込み時点から変更されていないことを確認する。
    opt 検証不成立：申請元の下書きが読み込み時点から変更されていないことを確認する。
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 409 / 他の操作で更新されました。最新の状態を確認してください。
    end
    end
    A->>F: 下書きに保存された画像配置を検証済みの配置値へ変換する。
    loop f.read_placements(row)
    A->>F: 現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。
    A->>D: 現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。
    A->>F: 現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。
    A->>D: 現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。
    A->>F: 添付画像のOCRが確認済みかつ利用可能であることを確認する。
    opt 検証不成立：添付画像のOCRが確認済みかつ利用可能であることを確認する。
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 409 / すべての画像のOCRを確認してください。
    end
    end
    A->>F: 添付画像の実体と記録済みハッシュを照合する。
    A->>S: 実体を取得・ハッシュ照合
    A->>F: 確認済みOCRの実体と記録済みハッシュを照合する。
    A->>S: 実体を取得・ハッシュ照合
    A->>F: 画像配置と確認済みの画像・OCRハッシュを一つのmanifest要素にする。
    end
    A->>F: 申請する本文の実体と記録済みハッシュを照合する。
    A->>S: 実体を取得・ハッシュ照合
    A->>F: 確定する本文と画像構成をmanifestのJSONへ変換する。
    A->>F: 下書きとmanifestから変更不能な確定版の行を組み立てる。
    A->>F: new_id
    A->>F: digest
    A->>F: now
    A->>F: 現在の組織の文書版を、版番号・本文の保存先・画像構成・検証用ハッシュを指定して登録する。
    A->>D: 現在の組織の文書版を、版番号・本文の保存先・画像構成・検証用ハッシュを指定して登録する。
    A->>F: 現在の組織の承認申請を、対象の文書版・申請者・審査状態・検証用ハッシュとともに登録する。
    A->>F: new_id
    A->>F: now
    A->>D: 現在の組織の承認申請を、対象の文書版・申請者・審査状態・検証用ハッシュとともに登録する。
    A->>F: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。
    A->>F: now
    A->>D: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。
    A->>F: 実行した変更の対象と結果を監査記録へ追加する。
    A->>F: audit
    A->>F: new_id
    A->>F: now
    A->>D: 現在の組織の監査記録として、操作した利用者・対象・変更前後の状態・理由を登録する。
    A->>F: 同じ要求を安全に再試行できるよう冪等キーと結果を記録する。
    A->>F: 冪等キーに処理内容と応答を保存する。
    A->>F: stable_id
    A->>F: digest
    A->>D: 現在の組織の操作の再送を判定するため、実行済み操作の入力ハッシュと応答を登録する。
    A->>F: 組織の更新競合を検出するための書込みフェンスを更新する。
    A->>F: 処理中に組織の状態が変更されていないことを確認する。
    A->>D: 組織の改訂番号が一致する場合だけ番号を進め、認可判定と権限失効の競合を検出する。
    opt 検証不成立：処理中に組織の状態が変更されていないことを確認する。
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 409 / 他の操作で更新されました。最新の状態を確認してください。
    end
    end
    A->>F: 公開する応答型で業務結果を検証し、レスポンスの境界を保証する。
    break 応答を返して終了
    Note over A,D: 成功応答前にtransactionをcommit・競合時rollback
    A-->>U: HTTP 201 / models.VersionsRow
    end
    Note over A,U: 共通例外経路（成功後に実行する追加処理ではない）
    opt 入力検証の失敗（RequestValidationError）
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 422 / 入力形式を確認してください。
    end
    end
    opt SQL実行またはcommitの競合（psycopg.Error）
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_REJECTED / 業務条件または入力検証によりリクエストを拒否しました。
    E-->>U: HTTP 409 / 競合しました。再読込してください。
    end
    end
    opt DB接続・外部サービスの失敗（捕捉して継続する場合を除く）
    break エラー応答を返して終了（後続の正常処理は実行しない）
    A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback
    E->>L: KR_HTTP_FAILED / 処理を完了できずエラー応答を返しました。
    E-->>U: HTTP 503 / 一時的に利用できません。
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
| 409 | idempotency_conflict | 同じ操作IDが異なる内容で使用されています。 | request_id |
| 409 | ocr_unconfirmed | すべての画像のOCRを確認してください。 | request_id |
| 422 | invalid_input | 入力形式を確認してください。 | request_id |
| 503 | unavailable | 一時的に利用できません。 | request_id |


**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.Context.document | 118 | Return | doc |
| kotorelay.context.Context.idempotent_result | 162 | If | not rows |
| kotorelay.context.Context.idempotent_result | 163 | Return | None |
| kotorelay.context.Context.idempotent_result | 170 | Return | record.response |
| kotorelay.context.new_id | 24 | Return | str(uuid4()) |
| kotorelay.context.now | 20 | Return | datetime.now(UTC) |
| kotorelay.context.stable_id | 28 | Return | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.objects.digest | 17 | Return | hashlib.sha256(data).hexdigest() |
| kotorelay.operations.documents.submit_version.functions.assets_get | 48 | Return | q.assets_get(ctx.db, q.AssetsGetParams(organization_id=ctx.org, id=placement.asset_id)) |
| kotorelay.operations.documents.submit_version.functions.build_manifest_image | 171 | Return | ManifestImage(placement=placement, image_hash=image_hash, ocr_hash=ocr_hash) |
| kotorelay.operations.documents.submit_version.functions.build_submit_version | 31 | Return | models.VersionsRow.model_validate_json(cached) |
| kotorelay.operations.documents.submit_version.functions.build_version | 84 | Return | models.VersionsRow(id=new_id(), organization_id=ctx.org, document_id=doc.id, number=doc.next_version, title=doc.title, body_key=row.body_key, body_hash=row.body_hash, manifest=manifest, manifest_hash=digest(manifest.encode()), created_by=ctx.user.id, created_at=now()) |
| kotorelay.operations.documents.submit_version.functions.check_concurrent_access | 161 | Return | ctx.fence() |
| kotorelay.operations.documents.submit_version.functions.document_doc | 21 | Return | ctx.document(str(document_id), 'author') |
| kotorelay.operations.documents.submit_version.functions.documents_update | 130 | Return | q.documents_update(ctx.db, q.DocumentsUpdateParams.model_validate(doc.model_copy(update={'next_version': doc.next_version + 1, 'revision': doc.revision + 1, 'updated_at': now()}), from_attributes=True)) |
| kotorelay.operations.documents.submit_version.functions.drafts_list | 36 | Return | q.drafts_list(ctx.db, q.DraftsListParams(organization_id=ctx.org)) |
| kotorelay.operations.documents.submit_version.functions.find_previous_result | 26 | Return | ctx.idempotent_result(str(key), 'submit', request) |
| kotorelay.operations.documents.submit_version.functions.has_previous_result | 181 | Return | bool(cached) |
| kotorelay.operations.documents.submit_version.functions.is_document_draft | 186 | Return | row.document_id == document_id |
| kotorelay.operations.documents.submit_version.functions.ocr_runs_get | 55 | Return | q.ocr_runs_get(ctx.db, q.OcrRunsGetParams(organization_id=ctx.org, id=placement.ocr_run_id)) |
| kotorelay.operations.documents.submit_version.functions.read_placements | 166 | Return | [Placement.model_validate(value) for value in json.loads(row.placements)] |
| kotorelay.operations.documents.submit_version.functions.record_submit_version_audit | 149 | Return | ctx.audit('submit', doc.id, version.id, 'draft', 'pending') |
| kotorelay.operations.documents.submit_version.functions.remember_submit_version_result | 156 | Return | ctx.remember(str(key), 'submit', request, version.model_dump_json()) |
| kotorelay.operations.documents.submit_version.functions.require_confirmed_ocr | 62 | Return | require(ocr.confirmed and ocr.status == 'ready', 'ocr_unconfirmed', 409) |
| kotorelay.operations.documents.submit_version.functions.serialize_manifest | 176 | Return | Manifest(body_hash=body_hash, images=images).model_dump_json() |
| kotorelay.operations.documents.submit_version.functions.submissions_insert | 110 | Return | q.submissions_insert(ctx.db, q.SubmissionsInsertParams(id=new_id(), organization_id=ctx.org, document_id=doc.id, version_id=version.id, requested_by=ctx.user.id, status='pending', manifest_hash=version.manifest_hash, decided_by=None, reason='', created_at=now(), decided_at=None)) |
| kotorelay.operations.documents.submit_version.functions.validate_draft_revision | 41 | Return | require(row.revision == data.revision, 'conflict', 409) |
| kotorelay.operations.documents.submit_version.functions.versions_insert | 101 | Return | q.versions_insert(ctx.db, q.VersionsInsertParams.model_validate(version, from_attributes=True)) |
| kotorelay.operations.documents.submit_version.response_builders.build_response | 10 | Return | TypeAdapter(ResponseData).validate_python(value) |
| kotorelay.operations.documents.submit_version.router.submit_version | 34 | If | f.has_previous_result(cached) |
| kotorelay.operations.documents.submit_version.router.submit_version | 35 | Return | build_response(f.build_submit_version(cast(str, cached))) |
| kotorelay.operations.documents.submit_version.router.submit_version | 39 | For | For |
| kotorelay.operations.documents.submit_version.router.submit_version | 55 | Return | build_response(version) |
| kotorelay.operations.system.authorization.functions.is_read_operation | 6 | Return | operation == 'read' |
