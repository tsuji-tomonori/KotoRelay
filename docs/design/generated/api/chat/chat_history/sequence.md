<!-- 実装から生成。直接編集しない。入力SHA256: 987c18a693c5fa5c9f59f732c65771f1c047c0829e22a5d72b689276aae93c56 -->

# 現行認可で会話履歴を再表示 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API
    participant D as PostgreSQLまたはDSQL
    participant S as S3実体
    participant M as Bedrock
    U->>A: GET /api/chat/{conversation_id}
    A->>D: 有効組織・所属を取得
    alt 認可条件が不成立
        A-->>U: 401または403または404
    else 許可
        A->>D: 現在の組織に属する回答履歴を識別子順に一覧取得する。
        A->>D: 現在の組織に属する指定の会話について、会話の所有者と開始日時を取得する。
        A->>D: 現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。
        A->>D: 現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を取得する。
        A->>D: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。
        A->>D: 現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。
        A->>D: 現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。
        A->>D: 現在の組織に属する部署を識別子順に一覧取得する。
        A->>D: 現在の組織に属する部署所属を識別子順に一覧取得する。
        A->>D: 現在の組織の組織名・改訂番号・利用停止状態を取得する。
        A->>D: 現在の組織に属する利用者を識別子順に一覧取得する。
        A->>S: 内容ハッシュ実体を照合
        opt 実体欠落・ハッシュ不一致
            A-->>U: 利用不可・回答保留
        end
        opt 有効根拠または索引配送
            A->>M: 上限付きモデル実行
            alt 外部サービス失敗
                M-->>A: 例外
                A->>D: 失敗状態を記録
            else 成功
                M-->>A: 結果
            end
        end
        A->>D: 必要な変更を確定（競合時rollback）
        A-->>U: 認可済み結果
    end
```

**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.Context.can_read | 71 | If | doc.status != 'active' or not self.memberships |
| kotorelay.context.Context.can_read | 72 | Return | False |
| kotorelay.context.Context.can_read | 73 | If | doc.visibility == 'organization' |
| kotorelay.context.Context.can_read | 74 | Return | True |
| kotorelay.context.Context.can_read | 75 | If | self.member(doc.department_id) |
| kotorelay.context.Context.can_read | 76 | Return | True |
| kotorelay.context.Context.can_read | 77 | Return | doc.visibility == 'selected' and any((self.member(department) for department in json.loads(doc.shared_departments))) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.objects.digest | 17 | Return | hashlib.sha256(data).hexdigest() |
| kotorelay.operations.chat.chat_history.functions.history | 15 | Return | [present(ctx, a) for a in sorted(q.answers_list(ctx.db, ctx.org), key=lambda a: a.created_at) if a.conversation_id == conversation_id] |
| kotorelay.operations.chat.chat_history.response_builders.build_response | 10 | Return | TypeAdapter(ResponseData).validate_python(value) |
| kotorelay.operations.chat.chat_history.router.chat_history | 24 | Return | build_response(f.history(ctx, str(conversation_id))) |
| kotorelay.operations.chat.shared.functions.present | 65 | Return | AnswerView(id=answer.id, conversation_id=answer.conversation_id, question=ctx.objects.get(answer.question_key).decode(), answer=ctx.objects.get(answer.answer_key).decode() if valid else '権限または公開版が変更されたため、この回答は表示できません。', status=answer.status if valid else 'hidden', citations=evidence.citations if valid else [], model=answer.model, created_at=answer.created_at) |
| kotorelay.operations.chat.shared.functions.validate_citation | 17 | If | not docs |
| kotorelay.operations.chat.shared.functions.validate_citation | 18 | Return | False |
| kotorelay.operations.chat.shared.functions.validate_citation | 20 | If | not ctx.can_read(doc) or doc.latest_version_id != citation.version_id or doc.revision != citation.document_revision |
| kotorelay.operations.chat.shared.functions.validate_citation | 25 | Return | False |
| kotorelay.operations.chat.shared.functions.validate_citation | 28 | If | not versions or not chunks |
| kotorelay.operations.chat.shared.functions.validate_citation | 29 | Return | False |
| kotorelay.operations.chat.shared.functions.validate_citation | 31 | If | not (digest(version.manifest.encode()) == version.manifest_hash and version.document_id == doc.id and chunk.ready and (chunk.version_id == version.id) and (chunk.document_id == doc.id) and (chunk.manifest_hash == version.manifest_hash == citation.manifest_hash) and (chunk.sha256 == citation.chunk_hash)) |
| kotorelay.operations.chat.shared.functions.validate_citation | 40 | Return | False |
| kotorelay.operations.chat.shared.functions.validate_citation | 41 | Try | Try |
| kotorelay.operations.chat.shared.functions.validate_citation | 46 | If | placements - {image.placement.id for image in manifest.images} |
| kotorelay.operations.chat.shared.functions.validate_citation | 47 | Return | False |
| kotorelay.operations.chat.shared.functions.validate_citation | 48 | For | For |
| kotorelay.operations.chat.shared.functions.validate_citation | 49 | If | image.placement.id in json.loads(chunk.placements) |
| kotorelay.operations.chat.shared.functions.validate_citation | 52 | If | not assets or not runs or (not runs[0].confirmed) or (runs[0].status != 'ready') |
| kotorelay.operations.chat.shared.functions.validate_citation | 53 | Return | False |
| kotorelay.operations.chat.shared.functions.validate_citation | 56 | Return | True |
| kotorelay.operations.chat.shared.functions.validate_citation | 57 | ExceptHandler | (Problem, ValueError) |
| kotorelay.operations.chat.shared.functions.validate_citation | 58 | Return | False |
