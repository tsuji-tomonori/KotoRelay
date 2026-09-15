<!-- 実装から生成。直接編集しない。入力SHA256: a4642be092686b22c6cb0bbcfdd011c0a0c93352fc1191e08d5c7dfccac4e973 -->

# 反映ジョブを再処理 — シーケンス

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
    U->>A: POST /api/operations/jobs/{job_id}
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
    A->>F: ジョブを実行できる運用権限を確認する。
    opt 検証不成立：ジョブを実行できる運用権限を確認する。
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 403 / この操作は許可されていません。
    end
    end
    A->>F: 現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を取得する。
    A->>D: 現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を取得する。
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
    A->>F: 実行対象のジョブが存在することを確認する。
    opt 検証不成立：実行対象のジョブが存在することを確認する。
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 404 / 対象を利用できません。
    end
    end
    A->>F: ジョブの再試行回数の上限を確認する。
    opt 検証不成立：ジョブの再試行回数の上限を確認する。
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 429 / 利用上限に達しました。
    end
    end
    A->>F: ジョブが完了または旧版として終了しているかを判定する。
    alt ジョブが完了または旧版として終了しているかを判定する。
    Note over A: 共有処理を終了して呼出し元へ結果を返す
    end
    rect rgb(245, 247, 250)
    Note over A: 例外を捕捉する処理範囲
    A->>F: ジョブが保存期間後の実体削除を要求しているかを判定する。
    alt ジョブが保存期間後の実体削除を要求しているかを判定する。
    A->>F: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。
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
    A->>F: 削除ジョブの対象文書が削除状態ではないかを判定する。
    alt 削除ジョブの対象文書が削除状態ではないかを判定する。
    Note over A: 共有処理を終了して呼出し元へ結果を返す
    end
    A->>F: 削除までの保存期間が経過していないかを判定する。
    A->>F: now
    alt 削除までの保存期間が経過していないかを判定する。
    Note over A: 共有処理を終了して呼出し元へ結果を返す
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
    A->>F: 現在の組織に属する添付画像を識別子順に一覧取得する。
    A->>D: 現在の組織に属する添付画像を識別子順に一覧取得する。
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
    A->>F: 現在の組織に属する文字認識の実行記録を識別子順に一覧取得する。
    A->>D: 現在の組織に属する文字認識の実行記録を識別子順に一覧取得する。
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
    A->>F: 現在の組織に属する下書きを識別子順に一覧取得する。
    A->>D: 現在の組織に属する下書きを識別子順に一覧取得する。
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
    A->>F: 現在の組織に属する文書版を識別子順に一覧取得する。
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
    A->>F: 現在の組織に属する回答履歴を識別子順に一覧取得する。
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
    A->>F: 処理対象の識別子を重複なく取り出す。
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
    A->>F: 削除文書の実体参照と、他文書・質問が引き続き使う保護対象を分類する。
    loop sorted(keys - protected)
    A->>F: 不要になった実体または検索索引を削除する。
    A->>S: 実体を削除
    opt 実体の入出力が失敗した場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    opt 実体サービスが失敗した場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    end
    A->>F: 用途と対象に一致するデータだけを取り出す。
    A->>F: 不要になった実体または検索索引を削除する。
    A->>M: delete
    opt モデル・検索サービスが失敗した場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    opt モデル・検索サービスが時間切れの場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    loop target_chunks[：100]
    A->>F: 現在の組織に属する指定の検索用の文書断片の記録を削除する。
    A->>D: 現在の組織に属する指定の検索用の文書断片の記録を削除する。
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
    A->>F: 一回の上限を超える削除対象の断片が残っているかを判定する。
    alt 一回の上限を超える削除対象の断片が残っているかを判定する。
    Note over A: 共有処理を終了して呼出し元へ結果を返す
    end
    A->>F: 用途と対象に一致するデータだけを取り出す。
    loop target_runs[：100]
    A->>F: 現在の組織に属する指定の文字認識の実行記録の記録を削除する。
    A->>D: 現在の組織に属する指定の文字認識の実行記録の記録を削除する。
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
    A->>F: 一回の上限を超える削除対象のOCR記録が残っているかを判定する。
    alt 一回の上限を超える削除対象のOCR記録が残っているかを判定する。
    Note over A: 共有処理を終了して呼出し元へ結果を返す
    end
    loop assets
    A->>F: 添付画像が削除対象の文書に属するかを判定する。
    alt 添付画像が削除対象の文書に属するかを判定する。
    A->>F: 現在の組織に属する指定の添付画像の記録を削除する。
    A->>D: 現在の組織に属する指定の添付画像の記録を削除する。
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
    end
    loop drafts
    A->>F: 下書きが削除対象の文書に属するかを判定する。
    alt 下書きが削除対象の文書に属するかを判定する。
    A->>F: 現在の組織に属する指定の下書きの記録を削除する。
    A->>D: 現在の組織に属する指定の下書きの記録を削除する。
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
    end
    Note over A: 共有処理を終了して呼出し元へ結果を返す
    else 条件不成立
    A->>F: 現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。
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
    A->>F: ジョブの対象版が現在の公開版ではないかを判定する。
    alt ジョブの対象版が現在の公開版ではないかを判定する。
    Note over A: 共有処理を終了して呼出し元へ結果を返す
    end
    A->>F: 用途と対象に一致するデータだけを取り出す。
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
    A->>F: 不要になった実体または検索索引を削除する。
    A->>M: delete
    opt モデル・検索サービスが失敗した場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    opt モデル・検索サービスが時間切れの場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    loop stale[：100]
    A->>F: 現在の組織に属する指定の検索用の文書断片の記録を削除する。
    A->>D: 現在の組織に属する指定の検索用の文書断片の記録を削除する。
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
    A->>F: 一回の削除上限を超える古い断片が残っているかを判定する。
    alt 一回の削除上限を超える古い断片が残っているかを判定する。
    Note over A: 共有処理を終了して呼出し元へ結果を返す
    end
    A->>F: 索引対象の文書が有効状態ではないかを判定する。
    alt 索引対象の文書が有効状態ではないかを判定する。
    Note over A: 共有処理を終了して呼出し元へ結果を返す
    end
    A->>F: 現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。
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
    A->>F: 後続処理に渡すデータを組み立てる。
    A->>F: 保存された実体をテキストへ復元する。
    A->>S: 実体を取得・ハッシュ照合
    opt 実体の欠落・ハッシュ不一致の場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    opt 実体の入出力が失敗した場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    opt 実体サービスが失敗した場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    A->>F: 用途と対象に一致するデータだけを取り出す。
    A->>F: 見出しと本文を検索用の長さに分割する。
    loop manifest.images
    A->>F: 現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。
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
    A->>F: 現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。
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
    A->>F: 記録された保存先から実体を取得してハッシュを照合する。
    A->>S: 実体を取得・ハッシュ照合
    opt 実体の欠落・ハッシュ不一致の場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    opt 実体の入出力が失敗した場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    opt 実体サービスが失敗した場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    A->>F: 後続処理に渡すデータを組み立てる。
    A->>S: 実体を取得・ハッシュ照合
    opt 実体の欠落・ハッシュ不一致の場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    opt 実体の入出力が失敗した場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    opt 実体サービスが失敗した場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    A->>F: OCRの領域順に本文を復元し、画像配置を付けた検索断片へ分割する。
    A->>F: 見出しと本文を検索用の長さに分割する。
    end
    A->>F: 生成する検索断片の件数上限を確認する。
    opt 検証不成立：生成する検索断片の件数上限を確認する。
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    A->>F: 取得したデータを識別子別に参照できる辞書へ変換する。
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
    loop enumerate(parts)
    A->>F: 本文または画像の実体を保存して内容ハッシュのキーを取得する。
    A->>S: 実体を保存
    opt 実体の入出力が失敗した場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    opt 実体サービスが失敗した場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    A->>F: 後続処理に渡すデータを組み立てる。
    A->>F: stable_id
    A->>F: 文書断片を検索エンジンへ登録する。
    A->>M: index
    opt モデル・検索サービスが失敗した場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    opt モデル・検索サービスが時間切れの場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    A->>F: 同じ識別子の検索断片が既に存在するかを判定する。
    alt 同じ識別子の検索断片が既に存在するかを判定する。
    A->>F: 現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を更新する。
    A->>D: 現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を更新する。
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
    A->>F: 現在の組織の検索用の文書断片を、出典の版・本文の保存先・画像配置とともに登録する。
    A->>D: 現在の組織の検索用の文書断片を、出典の版・本文の保存先・画像配置とともに登録する。
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
    end
    A->>F: 用途と対象に一致するデータだけを取り出す。
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
    A->>F: 保存件数と検索エンジンの反映状態が一致することを確認する。
    opt 前条件が成立
    A->>M: verify
    opt モデル・検索サービスが失敗した場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    opt モデル・検索サービスが時間切れの場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    end
    opt 検証不成立：保存件数と検索エンジンの反映状態が一致することを確認する。
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    loop actual
    A->>F: 記録された保存先から実体を取得してハッシュを照合する。
    A->>S: 実体を取得・ハッシュ照合
    opt 実体の欠落・ハッシュ不一致の場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    opt 実体の入出力が失敗した場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    opt 実体サービスが失敗した場合
    A->>L: KR_INDEX_FAILED / 索引または削除ジョブの実行が失敗しました。
    Note over A,U: 後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。
    A->>F: 後続処理に渡すデータを組み立てる。
    Note over A: 失敗した処理の残りを省略し、「現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。」から続ける。
    end
    A->>F: 現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を更新する。
    A->>D: 現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を更新する。
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
    Note over A: 共有処理を終了して呼出し元へ結果を返す
    end
    A->>F: 後続処理に渡すデータを組み立てる。
    end
    A->>F: 現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。
    A->>D: 現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。
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
    A->>F: 組織の更新競合を検出するための書込みフェンスを更新する。
    A->>F: 処理中に組織の状態が変更されていないことを確認する。
    A->>D: 組織の改訂番号が一致する場合だけ番号を進め、認可判定と権限失効の競合を検出する。
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
    opt 検証不成立：処理中に組織の状態が変更されていないことを確認する。
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 409 / 他の操作で更新されました。最新の状態を確認してください。
    end
    end
    Note over A: 共有処理を終了して呼出し元へ結果を返す
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
    A-->>U: HTTP 200 / models.OutboxRow
    end
```

**例外応答一覧（HTTP境界へ到達した場合）**

| HTTP | code | message | 相関ID |
| --- | --- | --- | --- |
| 401 | unauthenticated | ログインが必要です。 | request_id |
| 403 | forbidden | この操作は許可されていません。 | request_id |
| 404 | not_found | 対象を利用できません。 | request_id |
| 409 | conflict | 他の操作で更新されました。最新の状態を確認してください。 | request_id |
| 409 | conflict | 競合しました。再読込してください。 | request_id |
| 422 | invalid_input | 入力形式を確認してください。 | request_id |
| 422 | limit | 利用上限に達しました。 | request_id |
| 429 | limit | 利用上限に達しました。 | request_id |
| 503 | integrity | 保存内容の整合性を確認できません。 | request_id |
| 503 | unavailable | 一時的に利用できません。 | request_id |


**制御順序（関数内の行順）**

| 関数 | 行 | 要素 | 条件・早期終了・例外 |
| --- | --- | --- | --- |
| kotorelay.context.now | 20 | Return | datetime.now(UTC) |
| kotorelay.context.stable_id | 28 | Return | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.operational_logging.continuation_context | 150 | Return | OperationalLogContext(request_id=REQUEST_ID.get(), exception_type=type(error).__name__, status=None, code=(error.code if isinstance(error, Problem) else 'external_failure') if message_id == MessageId.INDEX_FAILED else None, message=CATALOG[message_id].response) |
| kotorelay.operations.indexing.retry_job.response_builders.build_response | 10 | Return | TypeAdapter(ResponseData).validate_python(value) |
| kotorelay.operations.indexing.retry_job.router.retry_job | 27 | Return | build_response(process(ctx, rt.engine, str(job_id))) |
| kotorelay.operations.indexing.shared.functions.answers_list | 285 | Return | q.answers_list(ctx.db, q.AnswersListParams(organization_id=ctx.org)) |
| kotorelay.operations.indexing.shared.functions.assets_delete | 348 | Return | q.assets_delete(ctx.db, q.AssetsDeleteParams(organization_id=ctx.org, id=asset.id)) |
| kotorelay.operations.indexing.shared.functions.assets_get | 109 | Return | q.assets_get(ctx.db, q.AssetsGetParams(organization_id=ctx.org, id=image.placement.asset_id)) |
| kotorelay.operations.indexing.shared.functions.assets_list | 265 | Return | q.assets_list(ctx.db, q.AssetsListParams(organization_id=ctx.org)) |
| kotorelay.operations.indexing.shared.functions.build_chunk | 168 | Return | models.ChunksRow(id=stable_id(version.id + str(number)), organization_id=ctx.org, document_id=doc.id, version_id=version.id, body_key=key, sha256=key, heading=heading, placements=placements, manifest_hash=version.manifest_hash, ready=False) |
| kotorelay.operations.indexing.shared.functions.build_manifest | 92 | Return | Manifest.model_validate_json(version.manifest) |
| kotorelay.operations.indexing.shared.functions.build_result | 134 | Return | OcrResult.model_validate_json(ctx.objects.get(run.result_key, image.ocr_hash)) |
| kotorelay.operations.indexing.shared.functions.build_updated | 388 | Return | job.model_copy(update={'status': status, 'attempts': job.attempts if status in {'retained', 'pending'} else job.attempts + 1, 'error_code': ''}) |
| kotorelay.operations.indexing.shared.functions.build_updated_2 | 399 | Return | job.model_copy(update={'status': 'failed', 'attempts': job.attempts + 1, 'error_code': exc.code}) |
| kotorelay.operations.indexing.shared.functions.build_updated_3 | 406 | Return | job.model_copy(update={'status': 'failed', 'attempts': job.attempts + 1, 'error_code': 'external_failure'}) |
| kotorelay.operations.indexing.shared.functions.check_concurrent_access | 420 | Return | ctx.fence() |
| kotorelay.operations.indexing.shared.functions.chunks_delete | 72 | Return | q.chunks_delete(ctx.db, q.ChunksDeleteParams(organization_id=ctx.org, id=stale_chunk.id)) |
| kotorelay.operations.indexing.shared.functions.chunks_delete_2 | 316 | Return | q.chunks_delete(ctx.db, q.ChunksDeleteParams(organization_id=ctx.org, id=chunk.id)) |
| kotorelay.operations.indexing.shared.functions.chunks_insert | 205 | Return | q.chunks_insert(ctx.db, q.ChunksInsertParams.model_validate(chunk, from_attributes=True)) |
| kotorelay.operations.indexing.shared.functions.chunks_list | 260 | Return | q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org)) |
| kotorelay.operations.indexing.shared.functions.chunks_update | 200 | Return | q.chunks_update(ctx.db, q.ChunksUpdateParams.model_validate(chunk, from_attributes=True)) |
| kotorelay.operations.indexing.shared.functions.chunks_update_2 | 233 | Return | q.chunks_update(ctx.db, q.ChunksUpdateParams.model_validate(current.model_copy(update={'ready': True}), from_attributes=True)) |
| kotorelay.operations.indexing.shared.functions.collect_live | 290 | Return | {d.id for d in q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org)) if d.status != 'deleted'} |
| kotorelay.operations.indexing.shared.functions.collect_object_keys | 472 | For | For |
| kotorelay.operations.indexing.shared.functions.collect_object_keys | 473 | For | For |
| kotorelay.operations.indexing.shared.functions.collect_object_keys | 474 | If | row.document_id == document_id |
| kotorelay.operations.indexing.shared.functions.collect_object_keys | 476 | If | row.document_id in live |
| kotorelay.operations.indexing.shared.functions.collect_object_keys | 478 | For | For |
| kotorelay.operations.indexing.shared.functions.collect_object_keys | 485 | Return | (keys, protected) |
| kotorelay.operations.indexing.shared.functions.decode_body | 97 | Return | ctx.objects.get(version.body_key, version.body_hash).decode() |
| kotorelay.operations.indexing.shared.functions.delete_build_index | 67 | Return | engine.delete([c.id for c in stale[:100]]) |
| kotorelay.operations.indexing.shared.functions.delete_purge | 299 | Return | ctx.objects.delete(key) |
| kotorelay.operations.indexing.shared.functions.delete_purge_2 | 311 | Return | engine.delete([c.id for c in target_chunks]) |
| kotorelay.operations.indexing.shared.functions.documents_get | 44 | Return | q.documents_get(ctx.db, q.DocumentsGetParams(organization_id=ctx.org, id=job.document_id)) |
| kotorelay.operations.indexing.shared.functions.documents_get_2 | 243 | Return | q.documents_get(ctx.db, q.DocumentsGetParams(organization_id=ctx.org, id=job.document_id)) |
| kotorelay.operations.indexing.shared.functions.drafts_delete | 358 | Return | q.drafts_delete(ctx.db, q.DraftsDeleteParams(organization_id=ctx.org, id=draft.id)) |
| kotorelay.operations.indexing.shared.functions.drafts_list | 275 | Return | q.drafts_list(ctx.db, q.DraftsListParams(organization_id=ctx.org)) |
| kotorelay.operations.indexing.shared.functions.enforce_chunk_limit | 139 | Return | require(len(parts) <= 300, 'limit', 422) |
| kotorelay.operations.indexing.shared.functions.enforce_retry_limit | 378 | Return | require(job.attempts < 5, 'limit', 429) |
| kotorelay.operations.indexing.shared.functions.has_more_stale_chunks | 77 | Return | bool(len(stale) > 100) |
| kotorelay.operations.indexing.shared.functions.has_more_target_chunks | 321 | Return | bool(len(target_chunks) > 100) |
| kotorelay.operations.indexing.shared.functions.has_more_target_ocr | 338 | Return | bool(len(target_runs) > 100) |
| kotorelay.operations.indexing.shared.functions.image_chunks | 430 | Return | [(image.placement.heading or heading, text, json.dumps([image.placement.id])) for heading, text in split_chunks(text or '添付画像')] |
| kotorelay.operations.indexing.shared.functions.index_build_index | 190 | Return | engine.index(chunk.id, text, doc.id, version.id) |
| kotorelay.operations.indexing.shared.functions.is_existing_chunk | 195 | Return | bool(chunk.id in previous) |
| kotorelay.operations.indexing.shared.functions.is_finished_job | 383 | Return | bool(job.status in {'done', 'obsolete'}) |
| kotorelay.operations.indexing.shared.functions.is_inactive_document | 82 | Return | bool(doc.status != 'active') |
| kotorelay.operations.indexing.shared.functions.is_obsolete_version | 51 | Return | bool(doc.latest_version_id != job.version_id or not job.version_id) |
| kotorelay.operations.indexing.shared.functions.is_purge_job | 438 | Return | job.kind == 'purge' |
| kotorelay.operations.indexing.shared.functions.is_restored_document | 250 | Return | bool(doc.status != 'deleted') |
| kotorelay.operations.indexing.shared.functions.is_target_asset | 343 | Return | bool(asset.document_id == doc.id) |
| kotorelay.operations.indexing.shared.functions.is_target_draft | 353 | Return | bool(draft.document_id == doc.id) |
| kotorelay.operations.indexing.shared.functions.is_within_retention | 255 | Return | bool((now() - job.created_at).total_seconds() < ctx.settings.retention_days * 86400) |
| kotorelay.operations.indexing.shared.functions.map_previous | 146 | Return | {c.id: c for c in q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org)) if c.version_id == version.id} |
| kotorelay.operations.indexing.shared.functions.ocr_runs_delete | 333 | Return | q.ocr_runs_delete(ctx.db, q.OcrRunsDeleteParams(organization_id=ctx.org, id=run.id)) |
| kotorelay.operations.indexing.shared.functions.ocr_runs_get | 118 | Return | q.ocr_runs_get(ctx.db, q.OcrRunsGetParams(organization_id=ctx.org, id=image.placement.ocr_run_id)) |
| kotorelay.operations.indexing.shared.functions.ocr_runs_list | 270 | Return | q.ocr_runs_list(ctx.db, q.OcrRunsListParams(organization_id=ctx.org)) |
| kotorelay.operations.indexing.shared.functions.outbox_get | 368 | Return | q.outbox_get(ctx.db, q.OutboxGetParams(organization_id=ctx.org, id=job_id)) |
| kotorelay.operations.indexing.shared.functions.outbox_update | 413 | Return | q.outbox_update(ctx.db, q.OutboxUpdateParams.model_validate(updated, from_attributes=True)) |
| kotorelay.operations.indexing.shared.functions.put_key | 155 | Return | ctx.objects.put(text.encode(), 'text/plain') |
| kotorelay.operations.indexing.shared.functions.require_job | 373 | Return | require(bool(rows)) |
| kotorelay.operations.indexing.shared.functions.require_operator | 363 | Return | require(ctx.user.operator, 'forbidden', 403) |
| kotorelay.operations.indexing.shared.functions.select_actual | 210 | Return | [c for c in q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org)) if c.version_id == version.id] |
| kotorelay.operations.indexing.shared.functions.select_parts | 102 | Return | [(heading, text, '[]') for heading, text in split_chunks(body)] |
| kotorelay.operations.indexing.shared.functions.select_stale | 58 | Return | [c for c in q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org)) if c.document_id == doc.id and (doc.status != 'active' or c.version_id != job.version_id)] |
| kotorelay.operations.indexing.shared.functions.select_target_chunks | 306 | Return | [c for c in chunks if c.document_id == doc.id] |
| kotorelay.operations.indexing.shared.functions.select_target_runs | 328 | Return | [r for r in runs if r.document_id == doc.id] |
| kotorelay.operations.indexing.shared.functions.split_chunks | 24 | For | For |
| kotorelay.operations.indexing.shared.functions.split_chunks | 25 | If | line.startswith('#') or len(buffer) + len(line) > 1200 |
| kotorelay.operations.indexing.shared.functions.split_chunks | 26 | If | buffer.strip() |
| kotorelay.operations.indexing.shared.functions.split_chunks | 29 | If | line.startswith('#') |
| kotorelay.operations.indexing.shared.functions.split_chunks | 31 | For | For |
| kotorelay.operations.indexing.shared.functions.split_chunks | 33 | If | len(buffer) + len(part) > 1200 and buffer.strip() |
| kotorelay.operations.indexing.shared.functions.split_chunks | 37 | If | buffer.strip() |
| kotorelay.operations.indexing.shared.functions.split_chunks | 39 | Return | chunks |
| kotorelay.operations.indexing.shared.functions.verify_index_completion | 221 | Return | require(len(actual) == len(parts) and engine.verify([c.id for c in actual]), 'integrity', 503) |
| kotorelay.operations.indexing.shared.functions.versions_get | 87 | Return | q.versions_get(ctx.db, q.VersionsGetParams(organization_id=ctx.org, id=version_id)) |
| kotorelay.operations.indexing.shared.functions.versions_list | 280 | Return | q.versions_list(ctx.db, q.VersionsListParams(organization_id=ctx.org)) |
| kotorelay.operations.indexing.shared.workflow.build_index | 20 | If | f.is_obsolete_version(doc, job) |
| kotorelay.operations.indexing.shared.workflow.build_index | 21 | Return | 'obsolete' |
| kotorelay.operations.indexing.shared.workflow.build_index | 24 | For | For |
| kotorelay.operations.indexing.shared.workflow.build_index | 26 | If | f.has_more_stale_chunks(stale) |
| kotorelay.operations.indexing.shared.workflow.build_index | 27 | Return | 'pending' |
| kotorelay.operations.indexing.shared.workflow.build_index | 28 | If | f.is_inactive_document(doc) |
| kotorelay.operations.indexing.shared.workflow.build_index | 29 | Return | 'done' |
| kotorelay.operations.indexing.shared.workflow.build_index | 34 | For | For |
| kotorelay.operations.indexing.shared.workflow.build_index | 42 | For | For |
| kotorelay.operations.indexing.shared.workflow.build_index | 46 | If | f.is_existing_chunk(previous, chunk) |
| kotorelay.operations.indexing.shared.workflow.build_index | 52 | For | For |
| kotorelay.operations.indexing.shared.workflow.build_index | 55 | Return | 'done' |
| kotorelay.operations.indexing.shared.workflow.process | 104 | If | f.is_finished_job(job) |
| kotorelay.operations.indexing.shared.workflow.process | 105 | Return | job |
| kotorelay.operations.indexing.shared.workflow.process | 106 | Try | Try |
| kotorelay.operations.indexing.shared.workflow.process | 109 | ExceptHandler | Problem |
| kotorelay.operations.indexing.shared.workflow.process | 114 | ExceptHandler | (OSError, BotoCoreError, ClientError) |
| kotorelay.operations.indexing.shared.workflow.process | 121 | Return | updated |
| kotorelay.operations.indexing.shared.workflow.purge | 61 | If | f.is_restored_document(doc) |
| kotorelay.operations.indexing.shared.workflow.purge | 62 | Return | 'obsolete' |
| kotorelay.operations.indexing.shared.workflow.purge | 63 | If | f.is_within_retention(ctx, job) |
| kotorelay.operations.indexing.shared.workflow.purge | 64 | Return | 'retained' |
| kotorelay.operations.indexing.shared.workflow.purge | 75 | For | For |
| kotorelay.operations.indexing.shared.workflow.purge | 79 | For | For |
| kotorelay.operations.indexing.shared.workflow.purge | 81 | If | f.has_more_target_chunks(target_chunks) |
| kotorelay.operations.indexing.shared.workflow.purge | 82 | Return | 'pending' |
| kotorelay.operations.indexing.shared.workflow.purge | 84 | For | For |
| kotorelay.operations.indexing.shared.workflow.purge | 86 | If | f.has_more_target_ocr(target_runs) |
| kotorelay.operations.indexing.shared.workflow.purge | 87 | Return | 'pending' |
| kotorelay.operations.indexing.shared.workflow.purge | 88 | For | For |
| kotorelay.operations.indexing.shared.workflow.purge | 89 | If | f.is_target_asset(asset, doc) |
| kotorelay.operations.indexing.shared.workflow.purge | 91 | For | For |
| kotorelay.operations.indexing.shared.workflow.purge | 92 | If | f.is_target_draft(draft, doc) |
| kotorelay.operations.indexing.shared.workflow.purge | 94 | Return | 'done' |
