# SQLと説明コメントの導入・完了契約

SQLを使うAPIの新規作成・再編・Dev標準導入と、説明コメントを追加・生成する変更で読む。既存の利用者指示が優先する。SQLを使わない実装へSQL層を追加しない。

## SQLの正本と責任

- 業務SQLはAPI operationごとの`sql/NNN_name.sql`を正本とし、1 file 1 statement、先頭に日本語の業務目的を置く。共通`repository.py`やrouter/functionsへSQL本文を直書き・集約しない。
- migration DDLとSQL ASTから引数・結果行の型と読込wrapperを`generated/queries.py`へ決定的に生成する。ファイルを置くだけ、手書きwrapper、`Any`による型の代用を生成完了としない。
- `functions.py`は生成wrapperをDB port経由で呼び出し、業務判定とtransaction境界を管理する。共通DB portは接続・実行の責任を持ち、API固有SQLを所有しない。
- 共通SQLから移す際はparameter binding、NULL、行数、戻り型、transactionと例外時rollbackの挙動を維持する。適用済みmigrationの本文・checksumを配置や翻訳のために変更しない。schema変更が必要なら新しいmigrationにする。
- query台帳とAPI別CRUDを実際のSQL・呼出関係から生成する。DDL由来のtable/ER設計も生成する。ファイル名やLLMの推測で対応を捏造しない。

同梱`designflow.py`は設計projectionであり、各DB driverの型付きquery generatorを自動提供するものではない。未接続なら導入先のgenerator/adapterを実装する。wrapper経由の呼出が同梱解析器で追えない場合も、実際の対応をadapterで抽出して検証し、追えないSQLを黙って除外しない。

## 日本語の説明

- 利用者から別言語の明示指示がなければ、新規・変更する説明コメント、module/class/function docstring、SQLの業務説明、生成コードの説明ヘッダーは日本語にする。既存コードの英語を新規生成の既定値にしない。
- 識別子、SQL keyword、API名、固有名詞、機械用lint指示、ライセンス原文は必要な原形を保つ。実行時の文字列をコメントと取り違えて翻訳しない。
- 生成物の英語はgenerator/templateを日本語に修正して再生成する。生成物の手修正や生成directoryを検査から一括除外する対応をしない。
- Python以外のTypeScript等にも説明言語の原則を適用する。対応言語のparser/linterまたは差分レビューを選び、Python用検査の成功で全言語検査済みとしない。

## 必須の検証と完了報告

導入時は実際のapplication root、説明コメントを持つ自作source root、migration rootを棚卸しする。SQLがある対象では次を関係する検査として必ず選ぶ。

1. 導入先dialectを設定したSQLFluff等のSQL lint。
2. 型付きquery生成の2回一致と、再生成せず差分を検出するcheck。生成物の削除、SQL/DDL変更、手編集を拒否することを回帰テストで確認する。
3. operation別SQL配置・inline SQL禁止・生成wrapperへの呼出境界、引数/行型とDDLの整合の検査。
4. 変更したSQLのDB統合テストと、業務transaction・rollbackの回帰テスト。
5. 日本語コメントと生成テンプレートの差分レビュー、生成コードを含む言語検査。
6. query台帳・API別CRUD・table/ER Markdownの生成と欠落・drift検査。

Python/SQL向けの補助検査例:

```sh
python tools/portable_python.py run <host-skill-path>/scripts/qualityflow.py -- source-conventions --root backend/src/app --root tools --root tests --sql-application-root backend/src/app
```

`--root`は説明言語を調べる自作Python/SQL sourceへ繰り返し指定する。vendorや参照標準の固定payload、ライセンス原文、適用済みmigrationを翻訳対象へ混ぜない。SQLを使わなければ`--sql-application-root`を省く。指定するapplication rootは共通repository層を含め、migrationとは分ける。構成が異なる導入先では同じ制約を検査するproject adapterを使い、対象を狭めて違反を隠さない。

application内にmigration管理用runnerがある場合は`--migration-runner backend/src/app/migrate.py`のように実在するfileを明示し、そのfileの移行台帳SQLだけを業務SQL配置検査から除外する。除外pathは実行結果へ表示する。採用前に業務SQLが混在していないことを確認し、理由を導入先の検査設定・既存PR欄等へ残す。directory全体や共通業務repositoryを除外しない。説明コメント検査はrunnerにも引き続き適用する。

このcommandは読み取り専用で、英語だけの説明、SQL配置違反、空/欠落wrapper、静的SQL文字列を非0終了で検出する。日本語文字の有無は言語品質の証明ではなく、ファイルの存在も型生成・到達可能性の証明ではない。動的SQL構築、型の意味、SQL方言、他言語はproject adapter・型検査・DBテスト・レビューで補完する。同梱SQL解析の未対応構文は未検証として解決し、成功へ読み替えない。

完了報告と必要な再開情報には、SQL正本・型生成元・生成先、説明言語、実行commandと結果、未対応範囲を残す。過去の会話で「対応済み」とあっても、現在のsourceと生成結果を確認する。SQL lintや型生成が未接続なら、単に既存CIが緑であることを完了根拠にしない。
