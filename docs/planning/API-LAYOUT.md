# API操作ごとの構成と責務

参照は[lazunexのpublish_api](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/src/app/apis/apis/publish_api)。2026年9月13日の利用者指定に従い、`operations/<group>/<operation>/`を1 API操作の所有境界とする。

| ファイル | 責務と接続 |
| --- | --- |
| router.py | 1個のpath operation、HTTP入力、依存注入、業務関数と応答組立の呼出し順序 |
| functions.py | そのAPIに固有の業務判定、処理、永続化境界の呼出し |
| schemas.py | API固有の入力モデルと公開する応答型。共有値型はルートのschemas.py |
| response_builders.py | 公開する応答型の検証・変換。画像はPNGのHTTP応答を構築 |
| contract.py | operation ID、グループ、method/path、目的、認証方式。実ルートとの一致を検査 |
| samples.py | 実HTTPテストで再現する入力と応答の不変項目。OpenAPIと設計へ投影 |
| sql/*.sql | その責務が直接使用するSQL正本。日本語一文の役割コメントを保持 |
| generated/queries.py | DDLと上記SQLから生成する型付き実行関数 |

グループ直下のrouter.pyは各APIのルーター登録だけを担当する。APIから別APIへの直接依存は拒否する。共通の下書き読込、画像認可、回答根拠検証・表示は各グループの`shared/functions.py`に置き、その共有処理が実行するSQLも同じsharedの下へ置く。Contextが行う認可・監査・冪等性のSQLはsystem/authorization、初期データ投入はsystem/bootstrap、workerの配送候補取得はsystem/dispatchが所有する。接続・実行だけを担当するDB portへ業務SQLを置かない。

複数APIが直接使用する同形SQLは、それぞれの操作が所有する正本として分ける。生成設計のSQL識別はファイル名だけでなく所有グループ・操作を含め、同名SQLの上書きや混同を防ぐ。共通DDLから業務行型を`generated/models.py`へ生成し、各queryの専用RowはSELECTの投影が全列と一致するときだけその業務行型を継承する。SQLを直接実行しないAPIへ空のSQLやqueryを追加しない。参照先の`queries.py`は互換用再exportであり、この実装は`generated/queries.py`を直接参照するため設置しない。

FastAPI、psycopg、同期DB port、DSQL/PostgreSQL、既存のHTTP契約は維持する。成功応答前のcommit・競合時rollbackと、モデル呼出しをtransaction外で行い確定時に再認可する境界を維持する。参照先固有のSQLAlchemy、外部AWS制御API、エラーや副作用を転用しない。

サンプルにはhealthの成功と、認証情報がない各APIの拒否を定義する。動的なrequest_id等を除く期待項目を実HTTPで比較する。業務成功・認可・競合・副作用の検証は既存の業務単体・PostgreSQL・Compose E2Eが担当し、サンプルで業務の全分岐を網羅したとは扱わない。

`tools/project/api_layout.py`で1 operation 1 package、6責務ファイル、contractとOpenAPIの一致、samplesとresponse builderの接続、依存方向、routerへの集計・永続化詳細の混在を検査する。`tools/project/queries.py --check`はSQLごとの引数・行型・生成先と欠落・手編集・SQL変更のdriftを検査する。`tools/project/design.py`が実配置の責務一覧とAPI別6帳票・CRUD・呼出し追跡を再生成する。

前回はAPIの「operation」を部署・文書・チャット等のドメイングループと解釈し、複数操作を一つのrouter/functionsへ集約した。入力型とqueryも全体共通にした。標準のfastapi-contract.mdとsql-and-language.mdには既に操作単位の指示があり、私の適用と参照実装の比較が不十分だった。既存adapterはSQLの構文・型生成・設計の集合と差分を検査していたが、操作単位の所有先、責務ファイルと実呼出し、API間依存方向を検査していなかった。このためCI成功を構成の適合まで含むものとして扱ってしまった。今回、実構成に接続した検査を追加し、標準側へ明示的な構成profileと負例テストの整備を提案する。

原因と標準側の改善提案は[dev-standard issue #68](https://github.com/tsuji-tomonori/dev-standard/issues/68)へ報告済み。移動した実装を参照する既存要件のtraceも、各APIの新しい所有先へ更新する。

## routerのフローとSQLモデルの責務（2026年9月13日追補）

利用者の追加指定により、認可・冪等性・個別処理・更新・監査・結果返却の全体フローをrouterに置く。functionsへ全体フローを委譲しない。routerには分岐、例外処理、手順に必要な反復とtransactionの範囲を記述し、SQL実行、外部portの実行、値の変換や集計の詳細は名前を持つ個別関数へ分ける。索引APIとworkerが共有するフローは`indexing/shared/workflow.py`が所有し、`shared/functions.py`はその個別処理を提供する。既存のFastAPI依存transactionは成功応答前に確定する。チャットのモデル呼出しはtransactionの外で行い、入力直前・回答確定時の再認可を維持する。

SQL正本は`sql/NNN_name.sql`、生成境界は各責務の`generated/queries.py`とする。SQLに実際に束縛する引数だけを厳格なPydantic Paramsにし、DDLとSQL ASTの束縛位置から型を決める。SELECTには列を列挙し、その投影と別名とNULL制約から専用Rowを生成する。全列を取得するときだけ共通の業務行型と代入互換にし、部分投影には未取得列を持たせない。DBの戻り値を単一の全体行型で代用しない。MySQLやSQLAlchemyの構文は移植せず、PostgreSQL/DSQLとpsycopgのparameter bindingを使う。

シーケンスはrouterと実call graphのASTから呼出し順、条件、反復、例外、transactionを投影する。SQLを名前順に並べたり、実装にない外部呼出しやcommitを定型で追加しない。SQL矢印は正本の日本語一文コメントを使う。構文未対応は生成失敗として検出する。実装の条件式は図と制御構造表から追跡できる。

以前のファイル配置検査はfunctionsに残った全体フローを検出できず、型生成も全体行型を流用していた。追加検査はfunctionsのtransaction・routerへの逆依存・複数更新段階の集約を拒否し、routerの直接DB/provider実行を拒否する。SQL投影、引数の余剰・NULL、呼出し順と分岐の生成、負例の拒否をテストする。詳細な原因と標準側への改善提案は[dev-standard issue #69](https://github.com/tsuji-tomonori/dev-standard/issues/69)へ報告した。

## 例外応答・運用ログ・テスト説明（2026年9月13日追補）

lazunexの`list_apis/functions.py`と`core/logging.py`を確認し、運用ログに独自型を必須とする方式を適用する。`MessageId`と`OperationalLogContext`を必須にした`ops_logger.warning/error`を使用する。catalogには出力条件、例外型、返す応答、確認手順、復旧手順を日本語で持つ。未知項目、未登録ID、level不一致を拒否し、生の例外文・質問・本文・JWTを渡さない。

HTTP境界ではProblem、入力検証、DB競合・停止、外部サービス例外を安全なstatus/code/messageへ変換し、応答とログのrequest_idを一致させる。モデル失敗、OCR失敗、索引失敗、根拠の除外は内部で捕捉して継続する。途中のログに未確定のHTTP statusを確定値として記録せず、後続の再認可・保存が成功した場合の応答をcatalogに明記する。workerの索引処理にはHTTP応答がない。

シーケンスは実際のrequire/Problemの引数・既定値、try/catch、応答契約を読んで例外のstatus・code・message・ログを表示する。already_answeredは内部制御例外であり、既存回答を再取得して200を返す。catch内の再送出とHTTP終了を区別する。静的に解決できないProblemを汎用の説明で埋めず生成失敗とする。

単体テストのdocstringに、実際の試験を説明する日本語のGiven/When/Thenを記述する。API帳票の要因とケース詳細、pytestの実行一覧はこの説明を参照し、fixture名やassert式を説明の代用にしない。説明の欠落・重複は検査で拒否する。条件式の技術的な追跡は詳細設計とシーケンスの補助表を使う。

前回は呼出し順や章の一致を検査した一方、HTTP応答への変換と型付きログを適用範囲から落とし、テストのASTを説明として代用していた。原因・改善案は[dev-standard issue #70](https://github.com/tsuji-tomonori/dev-standard/issues/70)へ報告した。


## router専用宣言とtoolsの採用（2026年9月14日追補）

router.pyに定義できる関数はFastAPIへ登録したendpointだけとする。補助関数、入れ子関数、メソッド、クラス、lambdaを置かない。グループ直下は登録だけとし、実アプリへ未登録のendpointや未使用のrouterも検査する。チャット受付と確定、文書一覧、ジョブ一覧の全体フローは各endpointに展開する。並べ替えなど個別の変換はfunctionsへ置く。

索引配送はHTTP APIとworkerが同じ処理を実行するため、shared/workflow.pyに置く。ここはHTTP endpointを定義しない。functionsからrouter・workflowへの逆依存を拒否し、シーケンスgeneratorはworkflow内の分岐・例外・SQL呼出しも追跡する。チャットは受付commit、transaction外のモデル呼出し、確定時の再認可という順序を維持する。

lazunexのmain（096e1e580ab1c0670c57e4febad2bd9fdd4698ee）にあるsrc/tools全52ファイルを[採用一覧](../design/generated/TOOLING.md)へ記載する。正本はtools/project/tool_adoption.jsonと接続先の実装で、設計generatorが一覧と参照先を検査して生成する。参照先の規約05はendpointと処理順の責務を定めるが、補助関数を一律拒否する検査は確認できなかったため、本プロジェクトの明示制約として追加する。

source_policy.pyはrouterの宣言、応答builderの直接返却、業務関数の結果の単独破棄、定数bool、説明docstring、包括的な例外捕捉、業務層のHTTPExceptionを検査する。既存api_layout.pyから呼び出し、verifyのAPI責務配置結果と品質portalへ接続する。DB更新wrapperの既存int件数は破棄を許可するが、読取結果やboolは許可しない。検証のみの関数はNoneにする。値を変数に代入した後の全経路での使用証明まではこの検査の対象としない。

Pythonの型の絞り込み、allによる根拠検証、共有workflow、同期psycopgを維持する。lazunex固有のSQLAlchemy例外、命名辞書、hub-admin等の定数、固定の行数・複雑度上限は取り込まない。テストは実HTTP・実DB・実測coverageを使い、独立YAMLや生成された空テストを追加しない。既存CI・Pages公開・branch規則は維持する。

標準側の改善提案は[dev-standard issue #72](https://github.com/tsuji-tomonori/dev-standard/issues/72)に起票した。

標準の汎用source-conventionsのSQL配置検査は、全SQL所有先にrouter.pyとfunctions.pyを要求するため、既存のshared・認可・初期投入・worker配送の43 SQLを拒否する。本構成ではこれらはHTTP endpointではない。日本語説明は標準検査で確認し、SQL配置・所有先・型付き生成・呼出境界は既存project adapterのqueries.pyとapi_layout.py、実DB試験で確認する。汎用検査への共有責務profileの不足もIssue #72へ報告する。
