<!-- 実装から生成。直接編集しない。入力SHA256: f473ec4902a9e7cc973e702d4fbb05a99ce8c26a324da9a1f4592aab94dbd60c -->

# 閲覧可能な文書を検索 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API router
    participant F as 個別処理 functions
    participant L as 型付き運用ログ
    participant D as PostgreSQLまたはDSQL
    participant S as 内容ハッシュ実体
    participant M as モデル・検索エンジン
    U->>A: GET /api/documents
    opt 認証に失敗した場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 401 / ログインが必要です。
    end
    end
    opt リクエストの入力形式が不正な場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 422 / 入力形式を確認してください。
    end
    end
    A->>D: 依存注入でtransaction開始・組織と所属を確認
    opt DB接続で競合が発生した場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 409 / 競合しました。再読込してください。
    end
    end
    opt DB接続でDBを利用できない場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_FAILED
    A-->>U: HTTP 503 / 一時的に利用できません。
    end
    end
    A->>D: 現在の組織の組織名・改訂番号・利用停止状態を取得する。
    opt SQL実行で競合が発生した場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 409 / 競合しました。再読込してください。
    end
    end
    opt SQL実行でDBを利用できない場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_FAILED
    A-->>U: HTTP 503 / 一時的に利用できません。
    end
    end
    opt 検証不成立：有効な組織と利用者を確認し、最新の所属を読み込む。
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 401 / ログインが必要です。
    end
    end
    A->>D: 現在の組織に属する利用者を識別子順に一覧取得する。
    opt SQL実行で競合が発生した場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 409 / 競合しました。再読込してください。
    end
    end
    opt SQL実行でDBを利用できない場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_FAILED
    A-->>U: HTTP 503 / 一時的に利用できません。
    end
    end
    opt 検証不成立：有効な組織と利用者を確認し、最新の所属を読み込む。
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 401 / ログインが必要です。
    end
    end
    A->>D: 現在の組織に属する部署を識別子順に一覧取得する。
    opt SQL実行で競合が発生した場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 409 / 競合しました。再読込してください。
    end
    end
    opt SQL実行でDBを利用できない場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_FAILED
    A-->>U: HTTP 503 / 一時的に利用できません。
    end
    end
    A->>D: 現在の組織に属する部署所属を識別子順に一覧取得する。
    opt SQL実行で競合が発生した場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 409 / 競合しました。再読込してください。
    end
    end
    opt SQL実行でDBを利用できない場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_FAILED
    A-->>U: HTTP 503 / 一時的に利用できません。
    end
    end
    A->>F: 一覧を絞り込む部署が指定されている。
    A->>F: 部署指定の管理用または執筆用の一覧かを判定する。
    alt 部署指定の管理用または執筆用の一覧かを判定する。
    A->>F: 指定した一覧の用途に対応する部署権限を確認する。
    A->>F: 指定した部署で要求された操作を実行できる。
    opt 検証不成立：指定した一覧の用途に対応する部署権限を確認する。
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 403 / この操作は許可されていません。
    end
    end
    end
    A->>F: 一覧を絞り込む部署が指定されている。
    alt 一覧を絞り込む部署が指定されている。
    A->>F: 現在の組織に属する文書を指定した所有部署で絞り込み、一覧の対象を取得する。
    A->>D: 現在の組織に属する文書を指定した所有部署で絞り込み、一覧の対象を取得する。
    opt SQL実行で競合が発生した場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 409 / 競合しました。再読込してください。
    end
    end
    opt SQL実行でDBを利用できない場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_FAILED
    A-->>U: HTTP 503 / 一時的に利用できません。
    end
    end
    else 条件不成立
    A->>F: 現在の組織に属する文書を識別子順に一覧取得する。
    A->>D: 現在の組織に属する文書を識別子順に一覧取得する。
    opt SQL実行で競合が発生した場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 409 / 競合しました。再読込してください。
    end
    end
    opt SQL実行でDBを利用できない場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_FAILED
    A-->>U: HTTP 503 / 一時的に利用できません。
    end
    end
    end
    A->>F: 管理用の文書一覧を要求しているかを判定する。
    alt 管理用の文書一覧を要求しているかを判定する。
    A->>F: 用途と対象に一致するデータだけを取り出す。
    loop docs
    A->>F: 指定した部署で要求された操作を実行できる。
    end
    else 条件不成立
    A->>F: 執筆用の文書一覧を要求しているかを判定する。
    alt 執筆用の文書一覧を要求しているかを判定する。
    A->>F: 用途と対象に一致するデータだけを取り出す。
    loop docs
    opt 前条件が成立
    A->>F: 指定した部署で要求された操作を実行できる。
    end
    end
    else 条件不成立
    A->>F: 用途と対象に一致するデータだけを取り出す。
    loop docs
    opt 前条件が成立
    A->>F: 現在の所属と公開範囲で文書を閲覧できる。
    A->>F: 指定した部署に現在も所属している。
    opt 前条件が成立
    loop json.loads(doc.shared_departments)
    A->>F: 指定した部署に現在も所属している。
    end
    end
    end
    end
    A->>F: 取得したデータを識別子別に参照できる辞書へ変換する。
    A->>D: 現在の組織に属する文書版を識別子順に一覧取得する。
    opt SQL実行で競合が発生した場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 409 / 競合しました。再読込してください。
    end
    end
    opt SQL実行でDBを利用できない場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_FAILED
    A-->>U: HTTP 503 / 一時的に利用できません。
    end
    end
    A->>F: 用途と対象に一致するデータだけを取り出す。
    end
    end
    A->>F: 用途と対象に一致するデータだけを取り出す。
    A->>F: 一覧の件数と次ページ情報が要求されている。
    A->>F: 更新日時の降順で並べた文書から指定範囲を切り出す。
    A->>F: 一覧の件数と次ページ情報が要求されている。
    alt 不成立：（一覧の件数と次ページ情報が要求されている。）
    A->>F: 公開する応答型で業務結果を検証し、レスポンスの境界を保証する。
    break 応答を返して終了
    A->>D: transactionをcommit
    opt commitで競合が発生した場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 409 / 競合しました。再読込してください。
    end
    end
    opt commitでDBを利用できない場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_FAILED
    A-->>U: HTTP 503 / 一時的に利用できません。
    end
    end
    A-->>U: HTTP 200 / list[models.DocumentsRow] | dict[str, object]
    end
    end
    A->>F: 取得したデータを識別子別に参照できる辞書へ変換する。
    A->>D: 現在の組織に属する文書版を識別子順に一覧取得する。
    opt SQL実行で競合が発生した場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 409 / 競合しました。再読込してください。
    end
    end
    opt SQL実行でDBを利用できない場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_FAILED
    A-->>U: HTTP 503 / 一時的に利用できません。
    end
    end
    A->>F: 現在の組織に属する承認申請を識別子順に一覧取得する。
    A->>D: 現在の組織に属する承認申請を識別子順に一覧取得する。
    opt SQL実行で競合が発生した場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 409 / 競合しました。再読込してください。
    end
    end
    opt SQL実行でDBを利用できない場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_FAILED
    A-->>U: HTTP 503 / 一時的に利用できません。
    end
    end
    A->>F: 現在の組織に属する検索用の文書断片を識別子順に一覧取得する。
    A->>D: 現在の組織に属する検索用の文書断片を識別子順に一覧取得する。
    opt SQL実行で競合が発生した場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 409 / 競合しました。再読込してください。
    end
    end
    opt SQL実行でDBを利用できない場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_FAILED
    A-->>U: HTTP 503 / 一時的に利用できません。
    end
    end
    loop docs[：limit]
    A->>F: 公開版・承認状態・索引状態・本文要約を一覧の一行へ組み立てる。
    A->>F: 用途と対象に一致するデータだけを取り出す。
    A->>F: 後続処理に渡すデータを組み立てる。
    A->>F: 公開版が存在し、閲覧用一覧に本文の要約を表示する。
    alt 公開版が存在し、閲覧用一覧に本文の要約を表示する。
    A->>S: 実体を取得・ハッシュ照合
    opt 実体の欠落・ハッシュ不一致の場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_FAILED
    A-->>U: HTTP 503 / 保存内容の整合性を確認できません。
    end
    end
    opt 実体の入出力が失敗した場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_FAILED
    A-->>U: HTTP 503 / 一時的に利用できません。
    end
    end
    opt 実体サービスが失敗した場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_FAILED
    A-->>U: HTTP 503 / 一時的に利用できません。
    end
    end
    else 条件不成立
    end
    end
    A->>F: 後続処理に渡すデータを組み立てる。
    A->>F: 公開する応答型で業務結果を検証し、レスポンスの境界を保証する。
    break 応答を返して終了
    A->>D: transactionをcommit
    opt commitで競合が発生した場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 409 / 競合しました。再読込してください。
    end
    end
    opt commitでDBを利用できない場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_FAILED
    A-->>U: HTTP 503 / 一時的に利用できません。
    end
    end
    A-->>U: HTTP 200 / list[models.DocumentsRow] | dict[str, object]
    end
```

**例外応答一覧（HTTP境界へ到達した場合）**

| HTTP | code | message | 相関ID |
| --- | --- | --- | --- |
| 401 | unauthenticated | ログインが必要です。 | request_id |
| 403 | forbidden | この操作は許可されていません。 | request_id |
| 409 | conflict | 競合しました。再読込してください。 | request_id |
| 422 | invalid_input | 入力形式を確認してください。 | request_id |
| 503 | unavailable | 一時的に利用できません。 | request_id |


**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.Context.can_read | 95 | If | doc.status != 'active' or not self.memberships |
| kotorelay.context.Context.can_read | 96 | Return | False |
| kotorelay.context.Context.can_read | 97 | If | doc.visibility == 'organization' |
| kotorelay.context.Context.can_read | 98 | Return | True |
| kotorelay.context.Context.can_read | 99 | If | self.member(doc.department_id) |
| kotorelay.context.Context.can_read | 100 | Return | True |
| kotorelay.context.Context.can_read | 101 | Return | doc.visibility == 'selected' and any((self.member(department) for department in json.loads(doc.shared_departments))) |
| kotorelay.context.Context.permission | 83 | For | For |
| kotorelay.context.Context.permission | 84 | If | m.department_id == department_id |
| kotorelay.context.Context.permission | 85 | Return | {'author': m.can_author, 'review': m.can_review, 'manage': m.leader, 'draft': m.can_author or m.can_review}.get(operation, False) |
| kotorelay.context.Context.permission | 91 | Return | False |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.operations.documents.list_documents.functions.build_document_item | 170 | Return | item |
| kotorelay.operations.documents.list_documents.functions.build_document_page | 131 | Return | {'published_number': version.number if version else None, 'approved_at': approval.decided_at if approval else None, 'index_ready': bool(version and any((c.version_id == version.id and c.ready for c in chunks))), 'summary': ctx.objects.get(typing.cast(q.VersionsListRow, version).body_key, typing.cast(q.VersionsListRow, version).body_hash).decode()[:180] if has_readable_summary(version, scope) else '', 'review_status': latest.status if latest and scope != 'read' else None, 'review_number': versions[latest.version_id].number if latest and scope != 'read' else None} |
| kotorelay.operations.documents.list_documents.functions.build_document_page_2 | 152 | Return | {'items': items, 'has_next': len(docs) > limit} |
| kotorelay.operations.documents.list_documents.functions.chunks_list | 111 | Return | q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org)) |
| kotorelay.operations.documents.list_documents.functions.documents_by_department | 31 | Return | q.documents_by_department(ctx.db, q.DocumentsByDepartmentParams(organization_id=ctx.org, department_id=department_id)) |
| kotorelay.operations.documents.list_documents.functions.documents_list | 38 | Return | q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org)) |
| kotorelay.operations.documents.list_documents.functions.has_department_filter | 182 | Return | bool(department_id) |
| kotorelay.operations.documents.list_documents.functions.has_readable_summary | 192 | Return | version is not None and scope == 'read' |
| kotorelay.operations.documents.list_documents.functions.is_authoring_scope | 55 | Return | bool(scope == 'work') |
| kotorelay.operations.documents.list_documents.functions.is_management_scope | 43 | Return | bool(scope == 'manage') |
| kotorelay.operations.documents.list_documents.functions.map_versions | 74 | Return | {v.id: v for v in q.versions_list(ctx.db, q.VersionsListParams(organization_id=ctx.org))} |
| kotorelay.operations.documents.list_documents.functions.map_versions_2 | 101 | Return | {v.id: v for v in q.versions_list(ctx.db, q.VersionsListParams(organization_id=ctx.org))} |
| kotorelay.operations.documents.list_documents.functions.paginate_documents | 177 | Return | sorted(docs, key=lambda doc: doc.updated_at, reverse=True)[offset:offset + limit] |
| kotorelay.operations.documents.list_documents.functions.requests_page | 187 | Return | page |
| kotorelay.operations.documents.list_documents.functions.require_department_permission | 22 | Return | require(ctx.permission(department_id, 'manage' if scope == 'manage' else 'draft'), 'forbidden', 403) |
| kotorelay.operations.documents.list_documents.functions.requires_department_permission | 15 | Return | bool(department_id and scope in {'manage', 'work'}) |
| kotorelay.operations.documents.list_documents.functions.select_docs | 50 | Return | [d for d in docs if ctx.permission(d.department_id, 'manage')] |
| kotorelay.operations.documents.list_documents.functions.select_docs_2 | 62 | Return | [d for d in docs if d.status != 'deleted' and ctx.permission(d.department_id, 'draft')] |
| kotorelay.operations.documents.list_documents.functions.select_docs_3 | 69 | Return | [d for d in docs if d.latest_version_id and ctx.can_read(d)] |
| kotorelay.operations.documents.list_documents.functions.select_docs_4 | 81 | Return | [d.model_copy(update={'title': versions[d.latest_version_id].title}) for d in docs if d.latest_version_id in versions] |
| kotorelay.operations.documents.list_documents.functions.select_docs_5 | 92 | Return | [d for d in docs if search.casefold() in d.title.casefold() and (not status or d.status == status)] |
| kotorelay.operations.documents.list_documents.functions.select_history | 118 | Return | [s for s in submissions if s.document_id == doc.id] |
| kotorelay.operations.documents.list_documents.functions.submissions_list | 106 | Return | q.submissions_list(ctx.db, q.SubmissionsListParams(organization_id=ctx.org)) |
| kotorelay.operations.documents.list_documents.response_builders.build_response | 10 | Return | TypeAdapter(ResponseData).validate_python(value) |
| kotorelay.operations.documents.list_documents.router.list_documents | 38 | If | f.requires_department_permission(department, scope) |
| kotorelay.operations.documents.list_documents.router.list_documents | 45 | If | f.is_management_scope(scope) |
| kotorelay.operations.documents.list_documents.router.list_documents | 47 | If | f.is_authoring_scope(scope) |
| kotorelay.operations.documents.list_documents.router.list_documents | 55 | If | not f.requests_page(page) |
| kotorelay.operations.documents.list_documents.router.list_documents | 56 | Return | build_response(docs) |
| kotorelay.operations.documents.list_documents.router.list_documents | 61 | For | For |
| kotorelay.operations.documents.list_documents.router.list_documents | 63 | Return | build_response(f.build_document_page_2(items, limit, docs)) |
