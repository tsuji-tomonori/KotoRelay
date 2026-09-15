<!-- 実装から生成。直接編集しない。入力SHA256: 065f3a0aaa159ee25b4b54797ae13bebd5e0deb08cdd00f2becc4afbe26e1319 -->

# 最新承認版の根拠で回答 — シーケンス

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
    U->>A: POST /api/chat
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
    rect rgb(245, 247, 250)
    Note over A: 例外を捕捉する処理範囲
    rect rgb(235, 245, 255)
    A->>D: transaction開始
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
    A->>D: 失敗したtransactionをrollback
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
    A->>D: 失敗したtransactionをrollback
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
    A->>F: 質問先部署への現在の所属を確認する。
    A->>F: 指定した部署に現在も所属している。
    opt 検証不成立：質問先部署への現在の所属を確認する。
    A->>D: 失敗したtransactionをrollback
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 403 / この操作は許可されていません。
    end
    end
    A->>F: stable_id
    A->>F: 現在の組織に属する指定の回答履歴について、質問・回答の保存先と根拠・回答状態を取得する。
    A->>D: 現在の組織に属する指定の回答履歴について、質問・回答の保存先と根拠・回答状態を取得する。
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
    A->>F: 同じ操作IDの回答が保存されている。
    alt 同じ操作IDの回答が保存されている。
    A->>F: 同じ冪等キーの質問内容・部署・会話が一致することを確認する。
    opt 前条件が成立
    A->>S: 実体を取得・ハッシュ照合
    opt 実体の欠落・ハッシュ不一致の場合
    A->>D: 失敗したtransactionをrollback
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
    end
    opt 検証不成立：同じ冪等キーの質問内容・部署・会話が一致することを確認する。
    A->>D: 失敗したtransactionをrollback
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 409 / 同じ操作IDが異なる内容で使用されています。
    end
    end
    A->>D: 失敗したtransactionをrollback
    rect rgb(235, 245, 255)
    A->>D: transaction開始
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
    A->>F: 現在の組織に属する指定の回答履歴について、質問・回答の保存先と根拠・回答状態を取得する。
    A->>D: 現在の組織に属する指定の回答履歴について、質問・回答の保存先と根拠・回答状態を取得する。
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
    A-->>U: HTTP 200 / AnswerView
    end
    end
    end
    A->>F: 要求内容の一致を確認して同じ冪等キーの記録済み結果を取得する。
    A->>F: 同じ冪等キーの処理内容が一致することを確認して保存済み応答を返す。
    A->>F: stable_id
    A->>D: 現在の組織に属する指定の再送判定の記録について、実行済み操作の入力ハッシュと応答を取得する。
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
    opt 前条件が成立
    A->>F: digest
    end
    opt 検証不成立：同じ冪等キーの処理内容が一致することを確認して保存済み応答を返す。
    A->>D: 失敗したtransactionをrollback
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 409 / 同じ操作IDが異なる内容で使用されています。
    end
    end
    A->>F: 現在の組織に属する利用イベントを識別子順に一覧取得する。
    A->>D: 現在の組織に属する利用イベントを識別子順に一覧取得する。
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
    A->>F: 再開要求を除いて利用者の当日質問数の上限を確認する。
    opt 検証不成立：再開要求を除いて利用者の当日質問数の上限を確認する。
    A->>D: 失敗したtransactionをrollback
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 429 / 利用上限に達しました。
    end
    end
    A->>F: 中断前に受付済みの会話がある。
    alt 中断前に受付済みの会話がある。
    else 条件不成立
    A->>F: 継続する会話が指定されている。
    alt 継続する会話が指定されている。
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
    A->>F: 会話が存在し現在の利用者が所有することを確認する。
    opt 検証不成立：会話が存在し現在の利用者が所有することを確認する。
    A->>D: 失敗したtransactionをrollback
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 404 / 対象を利用できません。
    end
    end
    A->>F: 会話内の回答が同じ部署に帰属することを確認する。
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
    opt 検証不成立：会話内の回答が同じ部署に帰属することを確認する。
    A->>D: 失敗したtransactionをrollback
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 409 / 利用部署を変更する場合は新しい会話を開始してください。
    end
    end
    else 条件不成立
    A->>F: new_id
    A->>F: 現在の組織の会話を、所有者と開始日時を指定して登録する。
    A->>F: now
    A->>D: 現在の組織の会話を、所有者と開始日時を指定して登録する。
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
    A->>F: 最新承認版を持ち現在閲覧できる文書を識別子別に取得する。
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
    loop q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org))
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
    A->>F: 閲覧可能な文書の範囲で質問に関連する断片を検索する。
    A->>M: search
    opt モデル・検索サービスが失敗した場合
    break エラー応答を返して終了
    A->>L: KR_HTTP_FAILED
    A-->>U: HTTP 503 / 一時的に利用できません。
    end
    end
    opt モデル・検索サービスが時間切れの場合
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
    loop f.chunks_list(ctx)
    A->>F: 閲覧可能な最新承認版の反映済み断片でないかを判定する。
    alt 閲覧可能な最新承認版の反映済み断片でないかを判定する。
    Note over A: この候補の処理を終了し、次の候補へ
    end
    A->>F: 検索エンジンの候補に含まれない断片かを判定する。
    alt 検索エンジンの候補に含まれない断片かを判定する。
    Note over A: この候補の処理を終了し、次の候補へ
    end
    rect rgb(245, 247, 250)
    Note over A: 例外を捕捉する処理範囲
    A->>F: 断片実体のハッシュを照合して本文を取得する。
    A->>S: 実体を取得・ハッシュ照合
    opt 実体の欠落・ハッシュ不一致の場合
    A->>L: KR_EVIDENCE_REJECTED / 整合性を確認できない回答根拠を除外しました。
    Note over A,U: HTTPエラーを直ちに返さず根拠を除外して継続。残る有効根拠により回答を返すかstatus=held、履歴はstatus=hidden。
    Note over A: この候補の処理を終了し、次の候補へ
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
    A->>F: 検索順位があれば順位を使い、ローカル検索では質問と本文の共通語数を得点にする。
    A->>F: 検索エンジンの順位がなく、ローカルの共通語数で採点する。
    alt 検索エンジンの順位がなく、ローカルの共通語数で採点する。
    A->>F: terms
    A->>F: terms
    else 条件不成立
    end
    A->>F: 質問と断片の関連度が採用基準を満たすかを判定する。
    opt 前条件が成立
    opt 前条件が不成立
    A->>F: terms
    end
    end
    end
    A->>F: 得点の降順と識別子の昇順で根拠候補を並べ、上位十件を取り出す。
    loop f.rank_candidates(scored)
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
    A->>F: 取得時点の文書・版・断片とハッシュを回答根拠の参照値にまとめる。
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
    alt 不成立：（閲覧権限・現行版・根拠の実体とハッシュが現在も有効かを判定する。）
    Note over A: この候補の処理を終了し、次の候補へ
    end
    A->>F: 確定版に記録された本文と画像の構成を読み取る。
    A->>F: 検索断片に関連付けられた画像だけを取り出す。
    A->>F: 根拠画像を追加するとモデル入力の画像数上限を超えるかを判定する。
    alt 根拠画像を追加するとモデル入力の画像数上限を超えるかを判定する。
    Note over A: この候補の処理を終了し、次の候補へ
    end
    loop related
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
    A->>F: 根拠画像のハッシュを照合してモデル入力用の実体を取得する。
    A->>S: 実体を取得・ハッシュ照合
    opt 実体の欠落・ハッシュ不一致の場合
    A->>D: 失敗したtransactionをrollback
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
    end
    A->>F: 回答に使用する根拠が五件に達したかを判定する。
    alt 回答に使用する根拠が五件に達したかを判定する。
    Note over A: 反復を終了
    end
    end
    A->>F: 既存の受付記録を再開する要求ではないかを判定する。
    alt 既存の受付記録を再開する要求ではないかを判定する。
    A->>F: 現在の組織の利用イベントとして、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を登録する。
    A->>F: now
    A->>D: 現在の組織の利用イベントとして、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を登録する。
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
    A->>F: 同じ要求を安全に再試行できるよう冪等キーと結果を記録する。
    A->>F: 冪等キーに処理内容と応答を保存する。
    A->>F: stable_id
    A->>F: digest
    A->>D: 現在の組織の操作の再送を判定するため、実行済み操作の入力ハッシュと応答を登録する。
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
    A->>D: 失敗したtransactionをrollback
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 409 / 他の操作で更新されました。最新の状態を確認してください。
    end
    end
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
    end
    end
    A->>F: 回答に使用する根拠候補がある。
    alt 回答に使用する根拠候補がある。
    rect rgb(235, 245, 255)
    A->>D: transaction開始
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
    A->>F: すべての根拠の閲覧権限と公開版が現在も有効である。
    loop citations
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
    alt 不成立：（すべての根拠の閲覧権限と公開版が現在も有効である。）
    A->>F: 失効した根拠とその本文・画像をモデル入力から除く。
    end
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
    end
    A->>F: 回答に使用する根拠候補がある。
    alt 回答に使用する根拠候補がある。
    rect rgb(245, 247, 250)
    Note over A: 例外を捕捉する処理範囲
    A->>F: 準備済みの本文と画像をモデルへ送り回答を取得する。
    A->>M: generate
    opt モデル・検索サービスが失敗した場合
    A->>L: KR_MODEL_FAILED / 回答モデルの呼出しが失敗しました。
    Note over A,U: 後続の再認可と保存が成功すればHTTP 200、AnswerView.status=failed、answer=現在利用できる根拠が不足しているため、回答を保留しました。
    Note over A: 失敗した処理の残りを省略し、「回答確定時点でも質問先部署への所属が有効であることを確認する。」から続ける。
    end
    opt モデル・検索サービスが時間切れの場合
    A->>L: KR_MODEL_FAILED / 回答モデルの呼出しが失敗しました。
    Note over A,U: 後続の再認可と保存が成功すればHTTP 200、AnswerView.status=failed、answer=現在利用できる根拠が不足しているため、回答を保留しました。
    Note over A: 失敗した処理の残りを省略し、「回答確定時点でも質問先部署への所属が有効であることを確認する。」から続ける。
    end
    end
    end
    end
    rect rgb(235, 245, 255)
    A->>D: transaction開始
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
    A->>F: 回答確定時点でも質問先部署への所属が有効であることを確認する。
    A->>F: 指定した部署に現在も所属している。
    opt 検証不成立：回答確定時点でも質問先部署への所属が有効であることを確認する。
    break エラー応答を返して終了
    A->>L: KR_HTTP_REJECTED
    A-->>U: HTTP 403 / この操作は許可されていません。
    end
    end
    A->>F: 回答に使用する根拠候補がある。
    opt 前条件が成立
    A->>F: すべての根拠の閲覧権限と公開版が現在も有効である。
    loop citations
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
    end
    A->>F: 生成失敗と根拠の有効性から回答状態・公開する根拠・利用者向け本文を決める。
    A->>F: 回答状態に対応する質問・回答実体の保存先と根拠の行を組み立てる。
    A->>S: 実体を保存
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
    A->>S: 実体を保存
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
    A->>F: now
    A->>F: 現在の組織の回答履歴として、質問者・利用部署・質問と回答の保存先・根拠を登録する。
    A->>D: 現在の組織の回答履歴として、質問者・利用部署・質問と回答の保存先・根拠を登録する。
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
    A->>F: 現在の組織の利用イベントとして、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を登録する。
    A->>F: stable_id
    A->>F: now
    A->>D: 現在の組織の利用イベントとして、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を登録する。
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
    A->>F: 回答根拠に寄与した文書の識別子を重複なく取り出す。
    loop f.collect_contributing_documents(citations)
    A->>F: 現在の組織の利用イベントとして、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を登録する。
    A->>F: stable_id
    A->>F: now
    A->>D: 現在の組織の利用イベントとして、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を登録する。
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
    A->>F: 実行した変更の対象と結果を監査記録へ追加する。
    A->>F: audit
    A->>F: new_id
    A->>F: now
    A->>D: 現在の組織の監査記録として、操作した利用者・対象・変更前後の状態・理由を登録する。
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
    A-->>U: HTTP 200 / AnswerView
    end
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
| 409 | conversation_department | 利用部署を変更する場合は新しい会話を開始してください。 | request_id |
| 409 | idempotency_conflict | 同じ操作IDが異なる内容で使用されています。 | request_id |
| 422 | invalid_input | 入力形式を確認してください。 | request_id |
| 429 | limit | 利用上限に達しました。 | request_id |
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
| kotorelay.context.Context.idempotent_result | 162 | If | not rows |
| kotorelay.context.Context.idempotent_result | 163 | Return | None |
| kotorelay.context.Context.idempotent_result | 170 | Return | record.response |
| kotorelay.context.Context.member | 79 | Return | any((m.department_id == department_id for m in self.memberships)) |
| kotorelay.context.new_id | 24 | Return | str(uuid4()) |
| kotorelay.context.now | 20 | Return | datetime.now(UTC) |
| kotorelay.context.stable_id | 28 | Return | str(uuid5(NAMESPACE_URL, 'kotorelay:' + value)) |
| kotorelay.engines.terms | 30 | Return | {value[i:i + 2] for i in range(max(0, len(value) - 1))} &#124; set(re.findall('[a-z0-9]+', value)) |
| kotorelay.errors.require | 13 | If | not condition |
| kotorelay.errors.require | 14 | Raise | Raise |
| kotorelay.objects.digest | 17 | Return | hashlib.sha256(data).hexdigest() |
| kotorelay.operational_logging.continuation_context | 150 | Return | OperationalLogContext(request_id=REQUEST_ID.get(), exception_type=type(error).__name__, status=None, code=(error.code if isinstance(error, Problem) else 'external_failure') if message_id == MessageId.INDEX_FAILED else None, message=CATALOG[message_id].response) |
| kotorelay.operations.chat.ask_question.functions.answers_get | 32 | Return | q.answers_get(ctx.db, q.AnswersGetParams(organization_id=ctx.org, id=exc.message)) |
| kotorelay.operations.chat.ask_question.functions.answers_get_2 | 52 | Return | q.answers_get(ctx.db, q.AnswersGetParams(organization_id=ctx.org, id=answer_id)) |
| kotorelay.operations.chat.ask_question.functions.answers_insert | 300 | Return | q.answers_insert(ctx.db, q.AnswersInsertParams.model_validate(row, from_attributes=True)) |
| kotorelay.operations.chat.ask_question.functions.assets_get | 217 | Return | q.assets_get(ctx.db, q.AssetsGetParams(organization_id=ctx.org, id=image.placement.asset_id)) |
| kotorelay.operations.chat.ask_question.functions.build_answer_record | 283 | Return | models.AnswersRow(id=prepared.answer_id, organization_id=ctx.org, conversation_id=prepared.conversation_id, user_id=ctx.user.id, department_id=prepared.department_id, question_key=ctx.objects.put(prepared.question.encode()), answer_key=ctx.objects.put(text.encode()), evidence=Evidence(citations=citations).model_dump_json(), status=status, model=engine.name, created_at=now()) |
| kotorelay.operations.chat.ask_question.functions.build_citation | 373 | Return | shared_schemas.Citation(document_id=doc.id, version_id=version.id, version_number=version.number, has_images=bool(json.loads(chunk.placements)), chunk_id=chunk.id, title=version.title, heading=chunk.heading, manifest_hash=version.manifest_hash, chunk_hash=chunk.sha256, document_revision=doc.revision) |
| kotorelay.operations.chat.ask_question.functions.check_concurrent_access | 266 | Return | ctx.fence() |
| kotorelay.operations.chat.ask_question.functions.chunks_list | 158 | Return | q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org)) |
| kotorelay.operations.chat.ask_question.functions.collect_contributing_documents | 325 | Return | {c.document_id for c in citations} |
| kotorelay.operations.chat.ask_question.functions.conversations_get | 103 | Return | q.conversations_get(ctx.db, q.ConversationsGetParams(organization_id=ctx.org, id=conversation_id)) |
| kotorelay.operations.chat.ask_question.functions.conversations_insert | 132 | Return | q.conversations_insert(ctx.db, q.ConversationsInsertParams(id=conversation_id, organization_id=ctx.org, user_id=ctx.user.id, created_at=now())) |
| kotorelay.operations.chat.ask_question.functions.discard_invalid_evidence | 37 | Return | prepared.model_copy(update={'citations': [], 'texts': [], 'images': []}) |
| kotorelay.operations.chat.ask_question.functions.enforce_daily_question_limit | 86 | Return | require(resumed is not None or sum((1 for e in events if e.user_id == ctx.user.id and e.kind == 'question' and (e.created_at.date() == today))) < ctx.settings.max_questions_per_day, 'limit', 429) |
| kotorelay.operations.chat.ask_question.functions.events_insert | 241 | Return | q.events_insert(ctx.db, q.EventsInsertParams(id=answer_id, organization_id=ctx.org, user_id=ctx.user.id, department_id=data.department_id, document_id=None, answer_id=None, kind='question', outcome='accepted', created_at=now())) |
| kotorelay.operations.chat.ask_question.functions.events_insert_2 | 307 | Return | q.events_insert(ctx.db, q.EventsInsertParams(id=stable_id(row.id + 'outcome'), organization_id=ctx.org, user_id=ctx.user.id, department_id=prepared.department_id, document_id=None, answer_id=row.id, kind='outcome', outcome=status, created_at=now())) |
| kotorelay.operations.chat.ask_question.functions.events_insert_3 | 336 | Return | q.events_insert(ctx.db, q.EventsInsertParams(id=stable_id(row.id + document_id), organization_id=ctx.org, user_id=ctx.user.id, department_id=prepared.department_id, document_id=document_id, answer_id=row.id, kind='contribution', outcome=status, created_at=now())) |
| kotorelay.operations.chat.ask_question.functions.events_list | 76 | Return | q.events_list(ctx.db, q.EventsListParams(organization_id=ctx.org)) |
| kotorelay.operations.chat.ask_question.functions.exceeds_image_limit | 210 | Return | bool(len(images) + len(related) > ctx.settings.max_model_images) |
| kotorelay.operations.chat.ask_question.functions.find_previous_result | 71 | Return | ctx.idempotent_result(key, 'ask', request) |
| kotorelay.operations.chat.ask_question.functions.generate_answer | 42 | Return | rt.engine.generate(prepared.question, prepared.texts, prepared.images) |
| kotorelay.operations.chat.ask_question.functions.has_answer_evidence | 425 | Return | bool(prepared.citations) |
| kotorelay.operations.chat.ask_question.functions.has_enough_citations | 231 | Return | bool(len(citations) >= 5) |
| kotorelay.operations.chat.ask_question.functions.has_prepared_conversation | 415 | Return | conversation_id is not None |
| kotorelay.operations.chat.ask_question.functions.has_previous_answer | 410 | Return | bool(rows) |
| kotorelay.operations.chat.ask_question.functions.has_requested_conversation | 420 | Return | bool(data.conversation_id) |
| kotorelay.operations.chat.ask_question.functions.has_sufficient_relevance | 184 | Return | bool(score > 0 and (vector_keys is not None or score >= max(1, len(terms(data.question)) * 0.3))) |
| kotorelay.operations.chat.ask_question.functions.has_valid_evidence | 432 | Return | all((evidence_functions.validate_citation(ctx, citation) for citation in citations)) |
| kotorelay.operations.chat.ask_question.functions.is_new_question | 236 | Return | bool(resumed is None) |
| kotorelay.operations.chat.ask_question.functions.is_outside_search_results | 172 | Return | bool(vector_keys is not None and chunk.id not in vector_keys) |
| kotorelay.operations.chat.ask_question.functions.is_unavailable_chunk | 163 | Return | bool(chunk.document_id not in docs or chunk.version_id != docs[chunk.document_id].latest_version_id or (not chunk.ready)) |
| kotorelay.operations.chat.ask_question.functions.is_unhandled_problem | 27 | Return | bool(exc.code != 'already_answered') |
| kotorelay.operations.chat.ask_question.functions.load_chunk_text | 177 | Return | ctx.objects.get(chunk.body_key, chunk.sha256).decode() |
| kotorelay.operations.chat.ask_question.functions.load_citation_image | 226 | Return | ctx.objects.get(asset.object_key, image.image_hash) |
| kotorelay.operations.chat.ask_question.functions.load_readable_documents | 142 | Return | {d.id: d for d in q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org)) if d.latest_version_id and ctx.can_read(d)} |
| kotorelay.operations.chat.ask_question.functions.parse_manifest | 196 | Return | Manifest.model_validate_json(version.manifest) |
| kotorelay.operations.chat.ask_question.functions.rank_candidates | 391 | Return | sorted(scored, key=lambda item: (-item[0], item[1].id))[:10] |
| kotorelay.operations.chat.ask_question.functions.record_finalize_audit | 354 | Return | ctx.audit('answer', after=status) |
| kotorelay.operations.chat.ask_question.functions.remember_prepare_result | 261 | Return | ctx.remember(key, 'ask', request, conversation_id) |
| kotorelay.operations.chat.ask_question.functions.require_conversation_owner | 112 | Return | require(bool(conversations) and conversations[0].user_id == ctx.user.id) |
| kotorelay.operations.chat.ask_question.functions.require_current_membership | 271 | Return | require(ctx.member(prepared.department_id), 'forbidden', 403) |
| kotorelay.operations.chat.ask_question.functions.require_question_membership | 47 | Return | require(ctx.member(data.department_id), 'forbidden', 403) |
| kotorelay.operations.chat.ask_question.functions.require_same_department | 119 | Return | require(all((a.department_id == data.department_id for a in q.answers_list(ctx.db, q.AnswersListParams(organization_id=ctx.org)) if a.conversation_id == conversation_id)), 'conversation_department', 409) |
| kotorelay.operations.chat.ask_question.functions.resolve_answer_outcome | 399 | Return | (status, evidence if status == 'answered' else [], answer if status == 'answered' else '現在利用できる根拠が不足しているため、回答を保留しました。') |
| kotorelay.operations.chat.ask_question.functions.score_chunk | 359 | Return | float(len(terms(question) & terms(text))) if uses_local_scoring(vector_keys) else float(len(typing.cast(list[str], vector_keys)) - typing.cast(list[str], vector_keys).index(chunk_id)) |
| kotorelay.operations.chat.ask_question.functions.search_vector_keys | 153 | Return | engine.search(data.question, list(docs)) |
| kotorelay.operations.chat.ask_question.functions.select_citation_images | 203 | Return | [i for i in manifest.images if i.placement.id in json.loads(chunk.placements)] |
| kotorelay.operations.chat.ask_question.functions.uses_local_scoring | 437 | Return | vector_keys is None |
| kotorelay.operations.chat.ask_question.functions.validate_repeated_question | 59 | Return | require(prior[0].user_id == ctx.user.id and ctx.objects.get(prior[0].question_key).decode() == data.question and (prior[0].department_id == data.department_id) and (data.conversation_id is None or data.conversation_id == prior[0].conversation_id), 'idempotency_conflict', 409) |
| kotorelay.operations.chat.ask_question.functions.versions_get | 191 | Return | q.versions_get(ctx.db, q.VersionsGetParams(organization_id=ctx.org, id=chunk.version_id)) |
| kotorelay.operations.chat.ask_question.response_builders.build_response | 10 | Return | TypeAdapter(ResponseData).validate_python(value) |
| kotorelay.operations.chat.ask_question.router.ask_question | 37 | Try | Try |
| kotorelay.operations.chat.ask_question.router.ask_question | 42 | If | f.has_previous_answer(prior) |
| kotorelay.operations.chat.ask_question.router.ask_question | 44 | Raise | Raise |
| kotorelay.operations.chat.ask_question.router.ask_question | 50 | If | f.has_prepared_conversation(resumed) |
| kotorelay.operations.chat.ask_question.router.ask_question | 52 | If | f.has_requested_conversation(data) |
| kotorelay.operations.chat.ask_question.router.ask_question | 64 | For | For |
| kotorelay.operations.chat.ask_question.router.ask_question | 65 | If | f.is_unavailable_chunk(docs, chunk) |
| kotorelay.operations.chat.ask_question.router.ask_question | 67 | If | f.is_outside_search_results(vector_keys, chunk) |
| kotorelay.operations.chat.ask_question.router.ask_question | 69 | Try | Try |
| kotorelay.operations.chat.ask_question.router.ask_question | 71 | ExceptHandler | Problem |
| kotorelay.operations.chat.ask_question.router.ask_question | 78 | If | f.has_sufficient_relevance(score, vector_keys, data) |
| kotorelay.operations.chat.ask_question.router.ask_question | 83 | For | For |
| kotorelay.operations.chat.ask_question.router.ask_question | 87 | If | not evidence_functions.validate_citation(ctx, citation) |
| kotorelay.operations.chat.ask_question.router.ask_question | 91 | If | f.exceeds_image_limit(images, related, ctx) |
| kotorelay.operations.chat.ask_question.router.ask_question | 93 | For | For |
| kotorelay.operations.chat.ask_question.router.ask_question | 98 | If | f.has_enough_citations(citations) |
| kotorelay.operations.chat.ask_question.router.ask_question | 100 | If | f.is_new_question(resumed) |
| kotorelay.operations.chat.ask_question.router.ask_question | 113 | ExceptHandler | Problem |
| kotorelay.operations.chat.ask_question.router.ask_question | 114 | If | f.is_unhandled_problem(exc) |
| kotorelay.operations.chat.ask_question.router.ask_question | 115 | Raise | Raise |
| kotorelay.operations.chat.ask_question.router.ask_question | 117 | Return | build_response(present(ctx, f.answers_get(ctx, exc)[0])) |
| kotorelay.operations.chat.ask_question.router.ask_question | 120 | If | f.has_answer_evidence(prepared) |
| kotorelay.operations.chat.ask_question.router.ask_question | 122 | If | not f.has_valid_evidence(ctx, prepared.citations) |
| kotorelay.operations.chat.ask_question.router.ask_question | 124 | If | f.has_answer_evidence(prepared) |
| kotorelay.operations.chat.ask_question.router.ask_question | 125 | Try | Try |
| kotorelay.operations.chat.ask_question.router.ask_question | 127 | ExceptHandler | (BotoCoreError, ClientError, TimeoutError) |
| kotorelay.operations.chat.ask_question.router.ask_question | 142 | For | For |
| kotorelay.operations.chat.ask_question.router.ask_question | 146 | Return | build_response(present(ctx, row)) |
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
