# APIの6帳票契約

APIを持つ導入先では全operationについて次の6帳票を生成する。参考形式は[rag-sampleのAPI帳票](https://github.com/tsuji-tomonori/rag-sample/tree/main/docs/spec/40.apis)。ファイル名の`_gen`／`.gen`や配置は既存generatorに合わせられるが、6種類の内容を省略しない。ログ・DB操作がないAPIでも該当帳票に実装に基づく非該当理由を出す。

| 帳票 | 必須内容 | 導出元 |
|---|---|---|
| detail-design | 目的、入力の型・取得元、正常前提、具体的DB・テーブルへの操作、操作の入力・出力・条件、応答項目の取得元、異常時の副作用 | OpenAPI、型定義、処理分岐、実行するSQL／データアクセス。関数名一覧やコード転載だけでは不可 |
| interface | OpenAPI（Swagger互換）のpath/method、認証、parameter、request、response、schema、制約、example、エラー。機械可読OpenAPIも保持 | アプリケーションがexportしたOpenAPI。$ref・継承されたsecurity等を欠落させない |
| messages | ログID、level、本文テンプレート、発生条件、出力項目と型・マスク規則、出力箇所、運用対応 | 実際のlogger呼出しと実行時に参照するcatalog。HTTPエラー一覧で代替しない |
| query | DB・schema・対象table/entity、SQL種別またはNoSQL操作、概要、引数と型、戻り値、検索・結合・更新条件、transaction | SQL AST＋DDL＋型付きquery／データアクセス実装。NoSQLをSQLと偽装しない |
| sequence | 呼び出し元、API、DB、実在する外部サービス間のMermaid sequenceDiagram。if/else、try/except、早期終了の順序 | 制御フロー。generated queries等の内部wrapperをparticipantとして列挙しない |
| unit-test | 要因一覧、各要因の要素、境界値・正常・異常・例外、各ケースの具体的Given/When/Then、期待ログ・DB/外部状態、実装済みtest node | 入出力制約、認証、分岐、依存先の失敗条件、要件に基づく期待値、テスト実装 |

「条件成立＝正常」と一律変換しない。異常を表すifや回復可能な例外もある。単一要因ずつ変えたケースを直積と呼ばない。必要な組合せは条件間の依存から決め、除外する到達不能ケースには根拠を残す。必須の全要因・要素→ケース→実在する単体テストを対応付け、欠落があればテストを実装してから完了する。nodeの実在はassertの妥当性や実行成功を証明しないため、期待値と副作用のassertをレビューし、対象テストを実行する。

## 生成の接続

既存generatorが全内容を満たす場合はそれを使用する。不足する場合はproject adapterを実装する。共通rendererは次で呼べる。

```sh
python tools/portable_python.py run <host-skill-path>/scripts/designflow.py -- api-documents --source-root src --openapi openapi.json --model api-model.json --test-root tests --out docs/design/generated/api
```

同じ引数に`--check`を付けると書換えずに比較する。出力はoperation IDのSHA-256先頭16桁＋帳票種別の`.gen.md`、索引`API_DOCUMENTS.gen.md`、Swagger用`OPENAPI.gen.json`、source digestを持つmanifest。索引から各帳票を開ける。別の既存配置を使う場合は既存generator/adapterの同等checkを使用する。

adapterはOpenAPI、AST/型、SQL/DDL、実行時catalog、テストの実装から下記JSONを再生成する。JSONを人手で設計の新しい正本にしない。説明・期待値など実装から決められない意味だけは要件や実行時metadataを参照し、構造と対応関係を実装で検証する。`source_sha256`を更新するだけのadapterは不可。全route・DB呼出し・ログ呼出し・分岐の抽出集合とモデルの集合を検査する。未解析の呼出しを「なし」とせず生成未完了にする。

既存`fastapi` subcommandは構造抽出の部品であり、この6帳票の完成版ではない。対応外のtry/except等はproject adapterで解析する。共通rendererは任意言語の抽出器でも汎用的な意味検証器でもなく、現在はportable pytestの非parametrize node集合を使用する。他言語やparameterized nodeには対象の実際のcollectionと対応するadapter検査を実装する。

## adapterモデル v1

rootは`schema_version: 1`、`source_sha256`、`operations`を持つ。`source_sha256`はsource-rootの全ファイル、test-rootの`test*.py`、OpenAPIのrepository相対path→SHA-256。削除・追加を含む実ファイル集合と一致しない古いモデルを拒否する。build/cacheはsource-rootの外へ出す。モデルのsource pathはsource-root内の実在ファイル・行に限定する。

| JSON項目 | 構造・必須項目 |
|---|---|
| operations[] | `id`=OpenAPI operationId、`summary`、`source`、`preconditions`、`errors`、以下の各配列と`sequence` |
| source | `{ "path": "src/items.py", "line": 12 }`。operation、resource、query、message、factorそれぞれに指定 |
| inputs[] / outputs[] | `name`、`type`、`description`、`origin`。空なら`no_inputs_reason`／`no_outputs_reason` |
| resources[] | `id`、`database`、`table`、`action`、`input`、`output`、`condition`、`query_id`、`source`。queryとDB・tableが一致 |
| queries[] | `id`、`database`、`table`、`kind`、`summary`、`conditions`、`returns`、`transaction`、`arguments[]`、`source` |
| arguments[] | `name`、`type`、`description`。空ならqueryの`no_arguments_reason` |
| messages[] | `id`、`level`、`template`、`condition`、`operator_action`、`fields[]`、`source` |
| fields[] | `name`、`type`、`description`、`masking`。空ならmessageの`no_fields_reason` |
| 空のresource/query/message配列 | operationに`no_resources_reason`／`no_queries_reason`／`no_messages_reason`を指定 |
| factors[] | `id`、`name`、`source`、`elements[]`。空配列不可 |
| elements[] | `id`、`description`、`expected`。空配列不可 |
| cases[] | `id`、`given`、`when`、`then`、`expected_logs`、`expected_data`、`covers`、`tests`。空配列不可 |
| covers | `[["F1", "exists"], ["F2", "authorized"]]`のような要因ID・要素IDの組。全要因の全要素が最低1ケースに対応 |
| tests | `["tests/test_items.py::test_get_item"]`のような実在するpytest node IDの配列。空配列不可 |
| sequence | `sequenceDiagram`から始まるMermaid本文。fenceや初期化directiveを入れない。adapterのcheckでMermaid構文と制御フローとの対応を検証 |

## 導入完了検査

`.dev-standard/design.json`の`surfaces.api`に、従来の`sources`、`markdown`、`generate`、`check`に加えて次を指定する。

- `openapi`: 実際にexportしたOpenAPI JSONのpath。
- `operation_documents`: operationId→`detail-design`、`interface`、`messages`、`query`、`sequence`、`unit-test`の各Markdown pathのmapping。全pathを`markdown`にも含める。

`check_design.py`はOpenAPIの全operationとmappingの集合一致、6種類すべての宣言と存在を検査する。既存のAPI契約はこのmappingを追加して移行する。rendererを使う場合の`check`は、adapterのモデル再構築結果との非破壊比較と`api-documents --check`を両方実行する入口にする。必要な帳票を1つ削除、API追加、SQL条件変更、ログ変更、テスト削除のfixtureで非0終了を確認する。単なるファイル存在検査を内容の完全性の証明として報告しない。
