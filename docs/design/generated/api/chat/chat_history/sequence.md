<!-- 実装から生成。直接編集しない。入力SHA256: 1c655589065a087f66d0ae05a6e0b777b889337ba2d8cca7542a2988c7248164 -->

# 現行認可で会話履歴を再表示 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API router
    participant F as 個別処理 functions
    participant D as PostgreSQLまたはDSQL
    participant S as 内容ハッシュ実体
    participant M as モデル・検索エンジン
    U->>A: GET /api/chat/{conversation_id}
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
    A->>F: 現在の組織に属する指定の会話について、会話の所有者と開始日時を取得する。
    A->>D: 現在の組織に属する指定の会話について、会話の所有者と開始日時を取得する。
    A->>F: 取得対象の会話を現在の利用者が所有していることを確認する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: 用途と対象に一致するデータだけを取り出す。
    A->>D: 現在の組織に属する回答履歴を識別子順に一覧取得する。
    loop sorted(q.answers_list(ctx.db, q.AnswersListParams(organization_id=ctx.org)), key=lambda a： a.created_at)
    opt a.conversation_id == str(conversation_id)
    A->>F: present
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    loop evidence.citations
    A->>F: validate_citation
    A->>D: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。
    A->>F: can_read
    A->>D: 現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。
    A->>D: 現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を取得する。
    A->>F: digest
    rect rgb(245, 247, 250)
    Note over A: 例外を捕捉する処理範囲
    A->>S: 実体を取得・ハッシュ照合
    A->>S: 実体を取得・ハッシュ照合
    loop manifest.images
    alt image.placement.id in json.loads(chunk.placements)
    A->>D: 現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。
    A->>D: 現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。
    A->>S: 実体を取得・ハッシュ照合
    A->>S: 実体を取得・ハッシュ照合
    end
    end
    end
    end
    A->>S: 実体を取得・ハッシュ照合
    alt valid
    A->>S: 実体を取得・ハッシュ照合
    else 条件不成立
    end
    end
    end
    A->>F: 公開する応答型で業務結果を検証し、レスポンスの境界を保証する。
    Note over A: この処理からreturn
    Note over A,D: 成功応答前に依存transactionをcommit・失敗時rollback
    A-->>U: HTTP応答
```

**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.Context.can_read | 89 | If | doc.status != 'active' or not self.memberships |
| kotorelay.context.Context.can_read | 90 | Return | False |
| kotorelay.context.Context.can_read | 91 | If | doc.visibility == 'organization' |
| kotorelay.context.Context.can_read | 92 | Return | True |
| kotorelay.context.Context.can_read | 93 | If | self.member(doc.department_id) |
| kotorelay.context.Context.can_read | 94 | Return | True |
| kotorelay.context.Context.can_read | 95 | Return | doc.visibility == 'selected' and any((self.member(department) for department in json.loads(doc.shared_departments))) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.objects.digest | 17 | Return | hashlib.sha256(data).hexdigest() |
| kotorelay.operations.chat.chat_history.functions.conversations_get | 18 | Return | q.conversations_get(ctx.db, q.ConversationsGetParams(organization_id=ctx.org, id=str(conversation_id))) |
| kotorelay.operations.chat.chat_history.functions.require_conversation_owner | 27 | Return | require(bool(conversations) and conversations[0].user_id == ctx.user.id) |
| kotorelay.operations.chat.chat_history.functions.select_chat_history | 34 | Return | [present(ctx, a) for a in sorted(q.answers_list(ctx.db, q.AnswersListParams(organization_id=ctx.org)), key=lambda a: a.created_at) if a.conversation_id == str(conversation_id)] |
| kotorelay.operations.chat.chat_history.response_builders.build_response | 10 | Return | TypeAdapter(ResponseData).validate_python(value) |
| kotorelay.operations.chat.chat_history.router.chat_history | 28 | Return | build_response(f.select_chat_history(ctx, conversation_id)) |
| kotorelay.operations.chat.shared.functions.present | 74 | Return | AnswerView(id=answer.id, conversation_id=answer.conversation_id, question=ctx.objects.get(answer.question_key).decode(), answer=ctx.objects.get(answer.answer_key).decode() if valid else '権限または公開版が変更されたため、この回答は表示できません。', status=answer.status if valid else 'hidden', citations=evidence.citations if valid else [], model=answer.model, created_at=answer.created_at) |
| kotorelay.operations.chat.shared.functions.validate_citation | 19 | If | not docs |
| kotorelay.operations.chat.shared.functions.validate_citation | 20 | Return | False |
| kotorelay.operations.chat.shared.functions.validate_citation | 22 | If | not ctx.can_read(doc) or doc.latest_version_id != citation.version_id or doc.revision != citation.document_revision |
| kotorelay.operations.chat.shared.functions.validate_citation | 27 | Return | False |
| kotorelay.operations.chat.shared.functions.validate_citation | 32 | If | not versions or not chunks |
| kotorelay.operations.chat.shared.functions.validate_citation | 33 | Return | False |
| kotorelay.operations.chat.shared.functions.validate_citation | 35 | If | not (digest(version.manifest.encode()) == version.manifest_hash and version.document_id == doc.id and chunk.ready and (chunk.version_id == version.id) and (chunk.document_id == doc.id) and (chunk.manifest_hash == version.manifest_hash == citation.manifest_hash) and (chunk.sha256 == citation.chunk_hash)) |
| kotorelay.operations.chat.shared.functions.validate_citation | 44 | Return | False |
| kotorelay.operations.chat.shared.functions.validate_citation | 45 | Try | Try |
| kotorelay.operations.chat.shared.functions.validate_citation | 50 | If | placements - {image.placement.id for image in manifest.images} |
| kotorelay.operations.chat.shared.functions.validate_citation | 51 | Return | False |
| kotorelay.operations.chat.shared.functions.validate_citation | 52 | For | For |
| kotorelay.operations.chat.shared.functions.validate_citation | 53 | If | image.placement.id in json.loads(chunk.placements) |
| kotorelay.operations.chat.shared.functions.validate_citation | 61 | If | not assets or not runs or (not runs[0].confirmed) or (runs[0].status != 'ready') |
| kotorelay.operations.chat.shared.functions.validate_citation | 62 | Return | False |
| kotorelay.operations.chat.shared.functions.validate_citation | 65 | Return | True |
| kotorelay.operations.chat.shared.functions.validate_citation | 66 | ExceptHandler | (Problem, ValueError) |
| kotorelay.operations.chat.shared.functions.validate_citation | 67 | Return | False |
