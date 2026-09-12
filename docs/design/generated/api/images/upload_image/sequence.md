<!-- 実装から生成。直接編集しない。入力SHA256: 31de213f242d3d7bf0d4f5957d4ef327aaacb2267a973d8e0adce1f1531ac7e1 -->

# 画像を添付して位置付きOCRを実行 — シーケンス

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

```mermaid
sequenceDiagram
    participant U as 利用者
    participant A as API
    participant D as PostgreSQLまたはDSQL
    participant S as S3実体
    participant M as Bedrock
    U->>A: POST /api/images/documents/{document_id}
    A->>D: 有効組織・所属を取得
    alt 認可条件が不成立
        A-->>U: 401または403または404
    else 許可
        A->>D: 現在の組織の文書に添付した画像の保存先・形式・寸法・検証用ハッシュを登録する。
        A->>D: 現在の組織に属する添付画像を識別子順に一覧取得する。
        A->>D: 現在の組織に属する部署を識別子順に一覧取得する。
        A->>D: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。
        A->>D: 現在の組織に属する部署所属を識別子順に一覧取得する。
        A->>D: 現在の組織の画像に対する文字認識の実行記録を、認識結果の保存先・検証用ハッシュ・確認状態とともに登録する。
        A->>D: 組織の改訂番号が一致する場合だけ番号を進め、認可判定と権限失効の競合を検出する。
        A->>D: 現在の組織の組織名・改訂番号・利用停止状態を取得する。
        A->>D: 現在の組織に属する利用者を識別子順に一覧取得する。
        A->>S: 内容ハッシュ実体を照合
        opt 実体欠落・ハッシュ不一致
            A-->>U: 利用不可・回答保留
        end
        A->>D: 必要な変更を確定（競合時rollback）
        A-->>U: 認可済み結果
    end
```

**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.Context.document | 90 | Return | doc |
| kotorelay.context.new_id | 22 | Return | str(uuid4()) |
| kotorelay.context.now | 18 | Return | datetime.now(UTC) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.operations.images.functions.normalize_image | 21 | Try | Try |
| kotorelay.operations.images.functions.normalize_image | 37 | Return | (value, image.width, image.height) |
| kotorelay.operations.images.functions.normalize_image | 38 | ExceptHandler | (UnidentifiedImageError, OSError, Image.DecompressionBombError) |
| kotorelay.operations.images.functions.normalize_image | 39 | Raise | Raise |
| kotorelay.operations.images.functions.run_ocr | 46 | Try | Try |
| kotorelay.operations.images.functions.run_ocr | 53 | ExceptHandler | (OSError, subprocess.TimeoutExpired, subprocess.CalledProcessError) |
| kotorelay.operations.images.functions.run_ocr | 54 | Return | OcrResult(regions=[], engine='tesseract-jpn-eng-v1', status='failed') |
| kotorelay.operations.images.functions.run_ocr | 56 | For | For |
| kotorelay.operations.images.functions.run_ocr | 58 | If | text |
| kotorelay.operations.images.functions.run_ocr | 71 | Return | OcrResult(regions=regions, engine='tesseract-jpn-eng-v1', status='ready') |
| kotorelay.operations.images.functions.upload | 111 | Return | {'asset': asset, 'ocr_run': run, 'ocr': result} |
| kotorelay.operations.images.router.upload_image | 22 | Return | f.upload(ctx, str(document_id), file.file.read(ctx.settings.max_image_bytes + 1)) |
