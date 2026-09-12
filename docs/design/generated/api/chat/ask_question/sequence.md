<!-- 実装から生成。直接編集しない。入力SHA256: 31de213f242d3d7bf0d4f5957d4ef327aaacb2267a973d8e0adce1f1531ac7e1 -->

# 最新承認版の根拠で回答 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API
    participant D as PostgreSQLまたはDSQL
    participant S as S3実体
    participant M as Bedrock
    U->>A: POST /api/chat
    A->>D: 有効組織・所属を取得
    alt 認可条件が不成立
        A-->>U: 401または403または404
    else 許可
        A->>D: 現在の組織に属する指定の回答履歴について、質問・回答の保存先と根拠・回答状態を取得する。
        A->>D: 現在の組織の回答履歴として、質問者・利用部署・質問と回答の保存先・根拠を登録する。
        A->>D: 現在の組織に属する回答履歴を識別子順に一覧取得する。
        A->>D: 現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。
        A->>D: 現在の組織の監査記録として、操作した利用者・対象・変更前後の状態・理由を登録する。
        A->>D: 現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を取得する。
        A->>D: 現在の組織に属する検索用の文書断片を識別子順に一覧取得する。
        A->>D: 現在の組織に属する指定の会話について、会話の所有者と開始日時を取得する。
        A->>D: 現在の組織の会話を、所有者と開始日時を指定して登録する。
        A->>D: 現在の組織に属する部署を識別子順に一覧取得する。
        A->>D: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。
        A->>D: 現在の組織に属する文書を識別子順に一覧取得する。
        A->>D: 現在の組織の利用イベントとして、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を登録する。
        A->>D: 現在の組織に属する利用イベントを識別子順に一覧取得する。
        A->>D: 現在の組織に属する指定の再送判定の記録について、実行済み操作の入力ハッシュと応答を取得する。
        A->>D: 現在の組織の操作の再送を判定するため、実行済み操作の入力ハッシュと応答を登録する。
        A->>D: 現在の組織に属する部署所属を識別子順に一覧取得する。
        A->>D: 現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。
        A->>D: 組織の改訂番号が一致する場合だけ番号を進め、認可判定と権限失効の競合を検出する。
        A->>D: 現在の組織の組織名・改訂番号・利用停止状態を取得する。
        A->>D: 現在の組織に属する利用者を識別子順に一覧取得する。
        A->>D: 現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。
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
| kotorelay.context.Context.can_read | 70 | If | doc.status != 'active' or not self.memberships |
| kotorelay.context.Context.can_read | 71 | Return | False |
| kotorelay.context.Context.can_read | 72 | If | doc.visibility == 'organization' |
| kotorelay.context.Context.can_read | 73 | Return | True |
| kotorelay.context.Context.can_read | 74 | If | self.member(doc.department_id) |
| kotorelay.context.Context.can_read | 75 | Return | True |
| kotorelay.context.Context.can_read | 76 | Return | doc.visibility == 'selected' and any((self.member(department) for department in json.loads(doc.shared_departments))) |
| kotorelay.context.Context.idempotent_result | 129 | If | not rows |
| kotorelay.context.Context.idempotent_result | 130 | Return | None |
| kotorelay.context.Context.idempotent_result | 137 | Return | record.response |
| kotorelay.context.Context.member | 56 | Return | any((m.department_id == department_id for m in self.memberships)) |
| kotorelay.context.new_id | 22 | Return | str(uuid4()) |
| kotorelay.context.now | 18 | Return | datetime.now(UTC) |
| kotorelay.context.stable_id | 26 | Return | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| kotorelay.engines.terms | 30 | Return | {value[i:i + 2] for i in range(max(0, len(value) - 1))} &#124; set(re.findall('[a-z0-9]+', value)) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.objects.digest | 17 | Return | hashlib.sha256(data).hexdigest() |
| kotorelay.operations.chat.functions.finalize | 254 | For | For |
| kotorelay.operations.chat.functions.finalize | 271 | Return | present(ctx, row) |
| kotorelay.operations.chat.functions.prepare | 78 | If | prior |
| kotorelay.operations.chat.functions.prepare | 87 | Raise | Raise |
| kotorelay.operations.chat.functions.prepare | 103 | If | resumed is not None |
| kotorelay.operations.chat.functions.prepare | 105 | If | data.conversation_id |
| kotorelay.operations.chat.functions.prepare | 133 | For | For |
| kotorelay.operations.chat.functions.prepare | 134 | If | chunk.document_id not in docs or chunk.version_id != docs[chunk.document_id].latest_version_id or (not chunk.ready) |
| kotorelay.operations.chat.functions.prepare | 140 | If | vector_keys is not None and chunk.id not in vector_keys |
| kotorelay.operations.chat.functions.prepare | 142 | Try | Try |
| kotorelay.operations.chat.functions.prepare | 144 | ExceptHandler | Problem |
| kotorelay.operations.chat.functions.prepare | 151 | If | score > 0 and (vector_keys is not None or score >= max(1, len(terms(data.question)) * 0.3)) |
| kotorelay.operations.chat.functions.prepare | 158 | For | For |
| kotorelay.operations.chat.functions.prepare | 173 | If | not validate_citation(ctx, citation) |
| kotorelay.operations.chat.functions.prepare | 177 | If | len(images) + len(related) > ctx.settings.max_model_images |
| kotorelay.operations.chat.functions.prepare | 179 | For | For |
| kotorelay.operations.chat.functions.prepare | 184 | If | len(citations) >= 5 |
| kotorelay.operations.chat.functions.prepare | 186 | If | resumed is None |
| kotorelay.operations.chat.functions.prepare | 203 | Return | Prepared(answer_id=answer_id, conversation_id=conversation_id, question=data.question, department_id=data.department_id, citations=citations, texts=texts, images=images) |
| kotorelay.operations.chat.functions.present | 278 | Return | AnswerView(id=answer.id, conversation_id=answer.conversation_id, question=ctx.objects.get(answer.question_key).decode(), answer=ctx.objects.get(answer.answer_key).decode() if valid else '権限または公開版が変更されたため、この回答は表示できません。', status=answer.status if valid else 'hidden', citations=evidence.citations if valid else [], model=answer.model, created_at=answer.created_at) |
| kotorelay.operations.chat.functions.validate_citation | 30 | If | not docs |
| kotorelay.operations.chat.functions.validate_citation | 31 | Return | False |
| kotorelay.operations.chat.functions.validate_citation | 33 | If | not ctx.can_read(doc) or doc.latest_version_id != citation.version_id or doc.revision != citation.document_revision |
| kotorelay.operations.chat.functions.validate_citation | 38 | Return | False |
| kotorelay.operations.chat.functions.validate_citation | 41 | If | not versions or not chunks |
| kotorelay.operations.chat.functions.validate_citation | 42 | Return | False |
| kotorelay.operations.chat.functions.validate_citation | 44 | If | not (digest(version.manifest.encode()) == version.manifest_hash and version.document_id == doc.id and chunk.ready and (chunk.version_id == version.id) and (chunk.document_id == doc.id) and (chunk.manifest_hash == version.manifest_hash == citation.manifest_hash) and (chunk.sha256 == citation.chunk_hash)) |
| kotorelay.operations.chat.functions.validate_citation | 53 | Return | False |
| kotorelay.operations.chat.functions.validate_citation | 54 | Try | Try |
| kotorelay.operations.chat.functions.validate_citation | 59 | If | placements - {image.placement.id for image in manifest.images} |
| kotorelay.operations.chat.functions.validate_citation | 60 | Return | False |
| kotorelay.operations.chat.functions.validate_citation | 61 | For | For |
| kotorelay.operations.chat.functions.validate_citation | 62 | If | image.placement.id in json.loads(chunk.placements) |
| kotorelay.operations.chat.functions.validate_citation | 65 | If | not assets or not runs or (not runs[0].confirmed) or (runs[0].status != 'ready') |
| kotorelay.operations.chat.functions.validate_citation | 66 | Return | False |
| kotorelay.operations.chat.functions.validate_citation | 69 | Return | True |
| kotorelay.operations.chat.functions.validate_citation | 70 | ExceptHandler | (Problem, ValueError) |
| kotorelay.operations.chat.functions.validate_citation | 71 | Return | False |
| kotorelay.operations.chat.router.ask_question | 18 | Return | service.ask(rt, subject, data, str(key)) |
| kotorelay.operations.chat.service.ask | 13 | Try | Try |
| kotorelay.operations.chat.service.ask | 16 | ExceptHandler | Problem |
| kotorelay.operations.chat.service.ask | 17 | If | exc.code != 'already_answered' |
| kotorelay.operations.chat.service.ask | 18 | Raise | Raise |
| kotorelay.operations.chat.service.ask | 20 | Return | f.present(ctx, q.answers_get(ctx.db, ctx.org, exc.message)[0]) |
| kotorelay.operations.chat.service.ask | 23 | If | prepared.citations |
| kotorelay.operations.chat.service.ask | 26 | If | not all((f.validate_citation(ctx, c) for c in prepared.citations)) |
| kotorelay.operations.chat.service.ask | 28 | If | prepared.citations |
| kotorelay.operations.chat.service.ask | 29 | Try | Try |
| kotorelay.operations.chat.service.ask | 31 | ExceptHandler | (BotoCoreError, ClientError, TimeoutError) |
| kotorelay.operations.chat.service.ask | 34 | Return | f.finalize(ctx, prepared, answer, rt.engine, failed) |
