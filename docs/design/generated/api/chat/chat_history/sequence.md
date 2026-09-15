<!-- 実装から生成。直接編集しない。入力SHA256: a4642be092686b22c6cb0bbcfdd011c0a0c93352fc1191e08d5c7dfccac4e973 -->

# 現行認可で会話履歴を再表示 — シーケンス

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
    U->>A: GET /api/chat/{conversation_id}
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
    A->>F: 現在の組織に属する指定の会話について、会話の所有者と開始日時を取得する。
    A->>D: 現在の組織に属する指定の会話について、会話の所有者と開始日時を取得する。
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
    A->>F: 取得対象の会話を現在の利用者が所有していることを確認する。
    opt 検証不成立：取得対象の会話を現在の利用者が所有していることを確認する。
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 404 / 対象を利用できません。
    end
    end
    A->>F: 用途と対象に一致するデータだけを取り出す。
    A->>D: 現在の組織に属する回答履歴を識別子順に一覧取得する。
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
    loop sorted(q.answers_list(ctx.db, q.AnswersListParams(organization_id=ctx.org)), key=lambda a： a.created_at)
    A->>F: 回答が表示対象の会話に属している。
    opt 回答が表示対象の会話に属している。
    A->>F: 現在の根拠の有効性に応じて回答履歴と引用の表示を組み立てる。
    opt 検証不成立：現在の根拠の有効性に応じて回答履歴と引用の表示を組み立てる。
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 404 / 対象を利用できません。
    end
    end
    loop evidence.citations
    A->>F: 閲覧権限・現行版・根拠の実体とハッシュが現在も有効かを判定する。
    A->>D: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。
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
    A->>F: 現在の所属と公開範囲で文書を閲覧できる。
    A->>F: 指定した部署に現在も所属している。
    opt 前条件が成立
    loop json.loads(doc.shared_departments)
    A->>F: 指定した部署に現在も所属している。
    end
    end
    A->>D: 現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。
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
    A->>D: 現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を取得する。
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
    A->>F: digest
    rect rgb(245, 247, 250)
    Note over A: 例外を捕捉する処理範囲
    A->>S: 実体を取得・ハッシュ照合
    opt 実体の欠落・ハッシュ不一致の場合
    A->>L: KR_EVIDENCE_REJECTED / 整合性を確認できない回答根拠を除外しました。
    Note over A,U: HTTPエラーを直ちに返さず根拠を除外して継続。残る有効根拠により回答を返すかstatus=held、履歴はstatus=hidden。
    Note over F,A: 失敗結果を呼出し元へ返し、この個別処理を終了する
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
    A->>S: 実体を取得・ハッシュ照合
    opt 実体の欠落・ハッシュ不一致の場合
    A->>L: KR_EVIDENCE_REJECTED / 整合性を確認できない回答根拠を除外しました。
    Note over A,U: HTTPエラーを直ちに返さず根拠を除外して継続。残る有効根拠により回答を返すかstatus=held、履歴はstatus=hidden。
    Note over F,A: 失敗結果を呼出し元へ返し、この個別処理を終了する
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
    opt 保存データの形式が不正な場合
    A->>L: KR_EVIDENCE_REJECTED / 整合性を確認できない回答根拠を除外しました。
    Note over A,U: HTTPエラーを直ちに返さず根拠を除外して継続。残る有効根拠により回答を返すかstatus=held、履歴はstatus=hidden。
    Note over F,A: 失敗結果を呼出し元へ返し、この個別処理を終了する
    end
    loop manifest.images
    A->>F: 画像が引用した文書断片に含まれている。
    alt 画像が引用した文書断片に含まれている。
    A->>D: 現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。
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
    A->>D: 現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。
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
    A->>S: 実体を取得・ハッシュ照合
    opt 実体の欠落・ハッシュ不一致の場合
    A->>L: KR_EVIDENCE_REJECTED / 整合性を確認できない回答根拠を除外しました。
    Note over A,U: HTTPエラーを直ちに返さず根拠を除外して継続。残る有効根拠により回答を返すかstatus=held、履歴はstatus=hidden。
    Note over F,A: 失敗結果を呼出し元へ返し、この個別処理を終了する
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
    A->>S: 実体を取得・ハッシュ照合
    opt 実体の欠落・ハッシュ不一致の場合
    A->>L: KR_EVIDENCE_REJECTED / 整合性を確認できない回答根拠を除外しました。
    Note over A,U: HTTPエラーを直ちに返さず根拠を除外して継続。残る有効根拠により回答を返すかstatus=held、履歴はstatus=hidden。
    Note over F,A: 失敗結果を呼出し元へ返し、この個別処理を終了する
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
    end
    end
    end
    end
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
    A->>F: 回答のすべての引用根拠が現在も有効である。
    alt 回答のすべての引用根拠が現在も有効である。
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
    A->>F: 回答のすべての引用根拠が現在も有効である。
    A->>F: 回答のすべての引用根拠が現在も有効である。
    end
    end
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
    A-->>U: HTTP 200 / list[AnswerView]
    end
```

**例外応答一覧（HTTP境界へ到達した場合）**

| HTTP | code | message | 相関ID |
| --- | --- | --- | --- |
| 401 | unauthenticated | ログインが必要です。 | request_id |
| 404 | not_found | 対象を利用できません。 | request_id |
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
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.objects.digest | 17 | Return | hashlib.sha256(data).hexdigest() |
| kotorelay.operational_logging.continuation_context | 150 | Return | OperationalLogContext(request_id=REQUEST_ID.get(), exception_type=type(error).__name__, status=None, code=(error.code if isinstance(error, Problem) else 'external_failure') if message_id == MessageId.INDEX_FAILED else None, message=CATALOG[message_id].response) |
| kotorelay.operations.chat.chat_history.functions.belongs_to_conversation | 46 | Return | answer.conversation_id == str(conversation_id) |
| kotorelay.operations.chat.chat_history.functions.conversations_get | 18 | Return | q.conversations_get(ctx.db, q.ConversationsGetParams(organization_id=ctx.org, id=str(conversation_id))) |
| kotorelay.operations.chat.chat_history.functions.require_conversation_owner | 27 | Return | require(bool(conversations) and conversations[0].user_id == ctx.user.id) |
| kotorelay.operations.chat.chat_history.functions.select_chat_history | 34 | Return | [present(ctx, a) for a in sorted(q.answers_list(ctx.db, q.AnswersListParams(organization_id=ctx.org)), key=lambda a: a.created_at) if belongs_to_conversation(a, conversation_id)] |
| kotorelay.operations.chat.chat_history.response_builders.build_response | 10 | Return | TypeAdapter(ResponseData).validate_python(value) |
| kotorelay.operations.chat.chat_history.router.chat_history | 28 | Return | build_response(f.select_chat_history(ctx, conversation_id)) |
| kotorelay.operations.chat.shared.functions.has_valid_evidence | 102 | Return | valid |
| kotorelay.operations.chat.shared.functions.is_cited_image | 97 | Return | image.placement.id in json.loads(chunk.placements) |
| kotorelay.operations.chat.shared.functions.present | 81 | Return | AnswerView(id=answer.id, conversation_id=answer.conversation_id, question=ctx.objects.get(answer.question_key).decode(), answer=ctx.objects.get(answer.answer_key).decode() if has_valid_evidence(valid) else '権限または公開版が変更されたため、この回答は表示できません。', status=answer.status if has_valid_evidence(valid) else 'hidden', citations=evidence.citations if has_valid_evidence(valid) else [], model=answer.model, created_at=answer.created_at) |
| kotorelay.operations.chat.shared.functions.validate_citation | 21 | If | not docs |
| kotorelay.operations.chat.shared.functions.validate_citation | 22 | Return | False |
| kotorelay.operations.chat.shared.functions.validate_citation | 24 | If | not ctx.can_read(doc) or doc.latest_version_id != citation.version_id or doc.revision != citation.document_revision |
| kotorelay.operations.chat.shared.functions.validate_citation | 29 | Return | False |
| kotorelay.operations.chat.shared.functions.validate_citation | 34 | If | not versions or not chunks |
| kotorelay.operations.chat.shared.functions.validate_citation | 35 | Return | False |
| kotorelay.operations.chat.shared.functions.validate_citation | 37 | If | not (digest(version.manifest.encode()) == version.manifest_hash and version.document_id == doc.id and chunk.ready and (chunk.version_id == version.id) and (chunk.document_id == doc.id) and (chunk.manifest_hash == version.manifest_hash == citation.manifest_hash) and (chunk.sha256 == citation.chunk_hash)) |
| kotorelay.operations.chat.shared.functions.validate_citation | 46 | Return | False |
| kotorelay.operations.chat.shared.functions.validate_citation | 47 | Try | Try |
| kotorelay.operations.chat.shared.functions.validate_citation | 52 | If | placements - {image.placement.id for image in manifest.images} |
| kotorelay.operations.chat.shared.functions.validate_citation | 53 | Return | False |
| kotorelay.operations.chat.shared.functions.validate_citation | 54 | For | For |
| kotorelay.operations.chat.shared.functions.validate_citation | 55 | If | is_cited_image(image, chunk) |
| kotorelay.operations.chat.shared.functions.validate_citation | 63 | If | not assets or not runs or (not runs[0].confirmed) or (runs[0].status != 'ready') |
| kotorelay.operations.chat.shared.functions.validate_citation | 64 | Return | False |
| kotorelay.operations.chat.shared.functions.validate_citation | 67 | Return | True |
| kotorelay.operations.chat.shared.functions.validate_citation | 68 | ExceptHandler | (Problem, ValueError) |
| kotorelay.operations.chat.shared.functions.validate_citation | 73 | Return | False |
