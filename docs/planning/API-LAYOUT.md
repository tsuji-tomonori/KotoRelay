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

グループ直下のrouter.pyは各APIのルーター登録だけを担当する。APIから別APIへの直接依存は拒否する。共通の下書き読込、画像認可、回答根拠検証・表示、索引配送は各グループの`shared/functions.py`に置き、その共有処理が実行するSQLも同じsharedの下へ置く。Contextが行う認可・監査・冪等性のSQLはsystem/authorization、初期データ投入はsystem/bootstrap、workerの配送候補取得はsystem/dispatchが所有する。接続・実行だけを担当するDB portへ業務SQLを置かない。

複数APIが直接使用する同形SQLは、それぞれの操作が所有する正本として分ける。生成設計のSQL識別はファイル名だけでなく所有グループ・操作を含め、同名SQLの上書きや混同を防ぐ。共通DDLからの行型は`generated/models.py`へ一度生成し、各queryから参照する。SQLを直接実行しないAPIへ空のSQLやqueryを追加しない。参照先の`queries.py`は互換用再exportであり、この実装は`generated/queries.py`を直接参照するため設置しない。

FastAPI、psycopg、同期DB port、DSQL/PostgreSQL、既存のHTTP契約は維持する。成功応答前のcommit・競合時rollbackと、モデル呼出しをtransaction外で行い確定時に再認可する境界を維持する。参照先固有のSQLAlchemy、外部AWS制御API、エラーや副作用を転用しない。

サンプルにはhealthの成功と、認証情報がない各APIの拒否を定義する。動的なrequest_id等を除く期待項目を実HTTPで比較する。業務成功・認可・競合・副作用の検証は既存の業務単体・PostgreSQL・Compose E2Eが担当し、サンプルで業務の全分岐を網羅したとは扱わない。

`tools/project/api_layout.py`で1 operation 1 package、6責務ファイル、contractとOpenAPIの一致、samplesとresponse builderの接続、依存方向、routerへの業務反復・永続化混在を検査する。`tools/project/queries.py --check`はSQLごとの引数・行型・生成先と欠落・手編集・SQL変更のdriftを検査する。`tools/project/design.py`が実配置の責務一覧とAPI別6帳票・CRUD・呼出し追跡を再生成する。

前回はAPIの「operation」を部署・文書・チャット等のドメイングループと解釈し、複数操作を一つのrouter/functionsへ集約した。入力型とqueryも全体共通にした。標準のfastapi-contract.mdとsql-and-language.mdには既に操作単位の指示があり、私の適用と参照実装の比較が不十分だった。既存adapterはSQLの構文・型生成・設計の集合と差分を検査していたが、操作単位の所有先、責務ファイルと実呼出し、API間依存方向を検査していなかった。このためCI成功を構成の適合まで含むものとして扱ってしまった。今回、実構成に接続した検査を追加し、標準側へ明示的な構成profileと負例テストの整備を提案する。

原因と標準側の改善提案は[dev-standard issue #68](https://github.com/tsuji-tomonori/dev-standard/issues/68)へ報告済み。移動した実装を参照する既存要件のtraceも、各APIの新しい所有先へ更新する。
