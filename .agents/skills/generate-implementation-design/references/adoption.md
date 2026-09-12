# 初回導入・生成欠落の復旧

Skillをコピーしただけでは導入完了ではない。実装を伴う導入依頼には生成器の接続と初回Markdown生成を含める。継続開発で未接続が判明した場合も、この手順で補う。

SQLを使うAPIでは[SQLと説明コメントの契約](sql-and-language.md)も適用する。API別SQLと型付きquery生成、SQL lint・境界・生成差分・関連DBテストを接続し、説明コメントと生成ヘッダーの日本語を生成元から検査する。

1. 実際のsource treeとbuild設定からAPI、data、infra、frontendおよび固有領域を棚卸しする。各領域の入力、必要なMarkdown、generate/check commandを導入先所有の`.dev-standard/design.json`へ記載する。既存の同等契約があれば変換して検査でき、二重管理しない。
2. 既存generatorを優先する。不足は配布generatorまたはproject adapterで実装する。SQL非採用はSQL出力の非該当理由であり、DynamoDB等のdata設計全体を省く理由ではない。対象が存在しない場合だけ`not-applicable`と理由を使う。技術的に生成できない対象は`blocked`とし、理由と残作業を報告して導入未完了を維持する。
3. 実装のbuild/export/synthを含む再実行可能なgenerate commandでMarkdownを生成する。同一入力の2回生成でbyte一致を確認する。JSONやdigest、ファイル一覧のみを人向け設計書の代わりにしない。
4. `python <host-skill-path>/scripts/check_design.py --root .`を実行する。契約欠落、未分類、blocked、必要なMarkdownの欠落・空、drift command失敗、checkによるMarkdown書換えを失敗とする。初回は隔離fixtureで設計書削除・実装変更に対する非0終了も確認する。
5. 導入先の既存verify/build入口にこの検査または同等の検査を接続する。CIを利用する開発依頼では既存CIからも同じ入口を呼ぶよう、そのprojectの規則・権限内で接続する。installer自体はCI設定を配布しない。CIがない場合はローカルで実行する。
6. 完了報告は対象revision、生成Markdownへのpath、実行commandと結果、非該当理由・未完了領域を示す。再開時はこの永続契約と実ファイルから再検査し、会話の「完了」やinstall receiptだけを信用しない。

APIは[6帳票契約](api-documents.md)に従い、全operationの6種類と`operation_documents`の対応を追加する。APIの説明が1ファイル存在するだけでは完了にしない。

## 必要な内容

固定の枚数を満たすために文書を分割しない。次の内容を実装から導出し、operation/table/stack等の実inventoryと生成対象集合の一致をadapterで検査する。

| 領域 | Markdownに含める内容 |
|---|---|
| API | 全operation一覧、各operationのrequest/response・認証・エラー・処理sequence・依存先・要件/test trace |
| data | 各table/entityの属性・key/index・制約、CRUD/access pattern、関係図。NoSQLでは物理・論理の関係を区別 |
| infra | 各stackのresource、parameter/output、参照関係、権限・event/data flow、運用制約、trace |
| frontend | route/screen、component、状態遷移・interaction、API依存、trace |

標準CDK generatorのresource/parameter一覧だけで上表全体を満たしたと主張しない。未対応内容をadapterで補う。手書き設計判断は別に置き、推測で実装の事実を埋めない。

## 契約例

以下はfrontendだけを持つprojectの例。実projectの入力・出力へ置換する。`markdown`には必要なファイルを個別列挙し、globだけで欠落を見逃さない。`generate`と`check`はshell文字列ではなくargv配列である。実装にない領域の理由もレビューする。

```json
{
  "schema_version": 1,
  "surfaces": {
    "api": {"status": "not-applicable", "reason": "HTTP APIを提供しない"},
    "data": {"status": "not-applicable", "reason": "永続データを持たない"},
    "infra": {"status": "not-applicable", "reason": "管理するIaCを持たない"},
    "frontend": {
      "status": "required",
      "sources": ["src"],
      "markdown": ["docs/design/generated/frontend/IMPLEMENTATION.gen.md"],
      "generate": ["npm", "run", "docs:generate"],
      "check": ["npm", "run", "docs:drift"]
    }
  }
}
```

commandはレビュー済みのローカル生成・drift検査を指定し、deploy等を含めない。checkは既存Markdownを書き換えず、同じ生成logicで比較する。`check_design.py`はgenerateを自動実行しないため、古い出力を修復してから合格にすることはない。自身を呼ぶcommandを`check`に指定しない。

この検査は宣言された対象の機械検証であり、未宣言領域や説明の意味的完全性を証明しない。source treeとの棚卸し、adapterの集合一致検査、内容レビューを併用する。任意commandの隔離や外部作用の検知を保証するものでもない。
