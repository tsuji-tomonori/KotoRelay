<!-- 実装から生成。直接編集しない。入力SHA256: e3cb305ddf380bd9917bab7f5404c8ac54c8511b8d91b58e7192aa0d5991c3cf -->

# manifestを確認して承認・却下 — sequence

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
        A->>D: audit_insert
        A->>D: departments_list
        A->>D: documents_get
        A->>D: documents_update
        A->>D: idempotency_get
        A->>D: idempotency_insert
        A->>D: memberships_list
        A->>D: organizations_fence
        A->>D: organizations_get
        A->>D: outbox_insert
        A->>D: submissions_get
        A->>D: submissions_update
        A->>D: users_list
        A->>D: versions_get
        A->>S: 内容ハッシュ実体を照合
        opt 実体欠落・ハッシュ不一致
            A-->>U: 利用不可・回答保留
        end
        A->>D: 必要な変更を確定（競合時rollback）
        A-->>U: 認可済み結果
    end
```

## 制御順序（関数内の行順）

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.Context.document | 90 | Return | doc |
| kotorelay.context.Context.idempotent_result | 129 | If | not rows |
| kotorelay.context.Context.idempotent_result | 130 | Return | None |
| kotorelay.context.Context.idempotent_result | 137 | Return | record.response |
| kotorelay.context.Context.version | 96 | If | not self.permission(doc.department_id, 'draft') |
| kotorelay.context.Context.version | 100 | Return | version |
| kotorelay.context.new_id | 22 | Return | str(uuid4()) |
| kotorelay.context.now | 18 | Return | datetime.now(UTC) |
| kotorelay.context.stable_id | 26 | Return | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.objects.digest | 17 | Return | hashlib.sha256(data).hexdigest() |
| kotorelay.operations.reviews.functions.decide | 36 | If | cached |
| kotorelay.operations.reviews.functions.decide | 37 | Return | q.SubmissionsRow.model_validate_json(cached) |
| kotorelay.operations.reviews.functions.decide | 54 | If | data.decision == 'approved' |
| kotorelay.operations.reviews.functions.decide | 58 | If | not previous or previous[0].number < version.number |
| kotorelay.operations.reviews.functions.decide | 86 | Return | updated |
| kotorelay.operations.reviews.router.decide_review | 27 | Return | f.decide(ctx, str(submission_id), data, str(key)) |
