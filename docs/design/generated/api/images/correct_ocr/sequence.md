<!-- 実装から生成。直接編集しない。入力SHA256: 1c655589065a087f66d0ae05a6e0b777b889337ba2d8cca7542a2988c7248164 -->

# OCRを訂正し新しいrunを保存 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API router
    participant F as 個別処理 functions
    participant D as PostgreSQLまたはDSQL
    participant S as 内容ハッシュ実体
    participant M as モデル・検索エンジン
    U->>A: POST /api/images/{asset_id}/ocr
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
    A->>F: 現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。
    A->>D: 現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。
    A->>F: 補正対象の添付画像が存在することを確認する。
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
    A->>F: 用途と対象に一致するデータだけを取り出す。
    A->>F: OCR領域の識別子に重複がないことを確認する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    loop data.regions
    A->>F: OCR領域が画像の正規化座標の範囲内に収まることを確認する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    end
    A->>F: 用途と対象に一致するデータだけを取り出す。
    loop data.regions
    opt 前条件が不成立
    A->>F: new_id
    end
    end
    A->>F: 本文または画像の実体を保存して内容ハッシュのキーを取得する。
    A->>S: 実体を保存
    A->>F: 後続処理に渡すデータを組み立てる。
    A->>F: new_id
    A->>F: now
    A->>F: 現在の組織の画像に対する文字認識の実行記録を、認識結果の保存先・検証用ハッシュ・確認状態とともに登録する。
    A->>D: 現在の組織の画像に対する文字認識の実行記録を、認識結果の保存先・検証用ハッシュ・確認状態とともに登録する。
    A->>F: 実行した変更の対象と結果を監査記録へ追加する。
    A->>F: audit
    A->>F: new_id
    A->>F: now
    A->>D: 現在の組織の監査記録として、操作した利用者・対象・変更前後の状態・理由を登録する。
    A->>F: 組織の更新競合を検出するための書込みフェンスを更新する。
    A->>F: fence
    A->>D: 組織の改訂番号が一致する場合だけ番号を進め、認可判定と権限失効の競合を検出する。
    A->>F: require
    alt not condition
    Note over A: 例外を送出し通常経路を終了
    end
    A->>F: 後続処理に渡すデータを組み立てる。
    A->>F: 公開する応答型で業務結果を検証し、レスポンスの境界を保証する。
    Note over A: この処理からreturn
    Note over A,D: 成功応答前に依存transactionをcommit・失敗時rollback
    A-->>U: HTTP応答
```

**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.Context.document | 111 | Return | doc |
| kotorelay.context.new_id | 23 | Return | str(uuid4()) |
| kotorelay.context.now | 19 | Return | datetime.now(UTC) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.operations.images.correct_ocr.functions.assets_get | 18 | Return | q.assets_get(ctx.db, q.AssetsGetParams(organization_id=ctx.org, id=str(asset_id))) |
| kotorelay.operations.images.correct_ocr.functions.build_correct_ocr | 108 | Return | {'ocr_run': run, 'ocr': result} |
| kotorelay.operations.images.correct_ocr.functions.build_run | 73 | Return | models.OcrRunsRow(id=new_id(), organization_id=ctx.org, document_id=asset.document_id, asset_id=asset.id, result_key=key, result_hash=key, engine=result.engine, status='ready', confirmed=data.confirmed, created_at=now()) |
| kotorelay.operations.images.correct_ocr.functions.check_concurrent_access | 101 | Return | ctx.fence() |
| kotorelay.operations.images.correct_ocr.functions.document_correct_ocr | 28 | Return | ctx.document(asset.document_id, 'author') |
| kotorelay.operations.images.correct_ocr.functions.ocr_runs_insert | 89 | Return | q.ocr_runs_insert(ctx.db, q.OcrRunsInsertParams.model_validate(run, from_attributes=True)) |
| kotorelay.operations.images.correct_ocr.functions.put_key | 62 | Return | ctx.objects.put(result.model_dump_json().encode(), 'application/json') |
| kotorelay.operations.images.correct_ocr.functions.record_correct_ocr_audit | 96 | Return | ctx.audit('ocr_correction', asset.document_id) |
| kotorelay.operations.images.correct_ocr.functions.require_asset | 23 | Return | require(bool(assets)) |
| kotorelay.operations.images.correct_ocr.functions.select_ids | 33 | Return | [r.region_id for r in data.regions if r.region_id is not None] |
| kotorelay.operations.images.correct_ocr.functions.select_result | 52 | Return | [r.model_copy(update={'region_id': r.region_id or new_id(), 'source': 'human', 'confidence': None}) for r in data.regions] |
| kotorelay.operations.images.correct_ocr.functions.validate_region_bounds | 43 | Return | require(region.x + region.width <= 1.000001 and region.y + region.height <= 1.000001, 'invalid_region', 422) |
| kotorelay.operations.images.correct_ocr.functions.validate_region_ids | 38 | Return | require(len(ids) == len(set(ids)), 'invalid_region', 422) |
| kotorelay.operations.images.correct_ocr.response_builders.build_response | 10 | Return | TypeAdapter(ResponseData).validate_python(value) |
| kotorelay.operations.images.correct_ocr.router.correct_ocr | 33 | For | For |
| kotorelay.operations.images.correct_ocr.router.correct_ocr | 46 | Return | build_response(f.build_correct_ocr(run, result)) |
