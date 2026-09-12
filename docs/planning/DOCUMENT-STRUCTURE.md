# 生成設計の章構成・階層・CRUD

2026年9月12日の利用者指定に従い、lazunexのコミット`096e1e580ab1c0670c57e4febad2bd9fdd4698ee`の[API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)と[CRUD対応表](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/30.crud)を構成の参照元とする。章の契約は`tools/project/api_documents.py`、内容の導出は`tools/project/design.py`が所有する。

| 帳票 | 章の順序 |
| --- | --- |
| 詳細設計 | 1. 正常系入力 / 2. 正常系前提 / 3. 正常系リソース変更 / 4. 正常系レスポンス |
| インターフェース | Headers / Path Parameters / Query Parameters / Data / Responses / Samples |
| ログメッセージ | API / 生成・検証方針 / メッセージ一覧 / ログ詳細 / strict検証で要求する項目 |
| クエリ | SQLファイルごとに SQL種別 / SQLの概要 / 利用するテーブル / 引数 / 戻り値 / 条件 |
| シーケンス | Mermaid図。実装の制御順序を補足する |
| 単体テスト詳細 | 0. Router層の暗黙処理 / 1. 要因ごとの要素 / 2. 直積したテストケース一覧 / 3. テスト詳細 |

API帳票の配置は`docs/design/generated/api/<group>/<operation>/<kind>.md`とする。グループとAPIの索引を生成し、既存の`API.md`から辿れるようにする。PagesもAPIグループ→API→帳票の階層と現在位置を表示し、検索時も親階層を保持する。内部の設計リンクは同じSPAで移動する。

`crud/`にはDB・オブジェクト保存・ベクトル索引のCSV、対応表、グループ別のMermaid図と抽出根拠を生成する。C/R/U/DはSQL ASTの変更先と参照先、および保存先の実呼出しから導出する。権限分岐等を含む静的な和集合であり、一回の実行で全操作が発生する意味ではない。固定のヘルスチェックは空欄になる。インフラ構築時だけのCognito操作等をAPIのCRUDへ混在させない。

構成の一致と意味の完全性は別に検査する。元実装にないHTTP example、ログラッパー、サービス、直積の網羅率を追加したようには記述しない。単体テスト帳票の直積章には現時点の実在ケースを載せ、完全な組合せ網羅を導出していない限界を明記する。

前回はproject adapterで独自の見出しを採用し、dev-standardの6帳票の存在・OpenAPIとの集合一致・生成差分を主な検査とした。参照帳票の章順や配置階層、CRUD集合を検証する契約がなく、標準の参考リンクを具体的な受入条件へ落とさなかった。今回、構成の契約と回帰検査を追加し、同じ問題をdev-standardのissueへ報告する。

原因と標準側の改善方針は[dev-standard issue #67](https://github.com/tsuji-tomonori/dev-standard/issues/67)へ報告済み。

SQL正本の先頭には、そのSQLが扱う対象と処理の役割を日本語一文で記載する。シーケンス図のSQL呼出しラベル、クエリ帳票の「SQLの概要」、型付きquery関数のdocstringは、この同じコメントから生成する。たとえば`answers_get`は「現在の組織に属する指定の回答履歴について、質問・回答の保存先と根拠・回答状態を取得する。」と表示する。SQL識別子はクエリ帳票の章名と実装への参照として保持する。先頭コメントの欠落、日本語のない説明、句点の欠落・複数文は生成時に拒否し、役割の正確さはSQL本文と照合して確認する。
