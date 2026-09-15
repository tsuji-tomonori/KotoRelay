<!-- 実装から生成。直接編集しない。入力SHA256: a4642be092686b22c6cb0bbcfdd011c0a0c93352fc1191e08d5c7dfccac4e973 -->

# 死活確認 — 詳細設計

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## 1. 正常系入力

目的: 死活確認。

**Headers**

該当する入力はありません。

このoperationは認証を要求しません。

**Path Parameters**

該当する入力はありません。

**Query Parameters**

該当する入力はありません。

**Data**

リクエスト本文はありません。

## 2. 正常系前提

認証・認可と型制約を満たすこと。以下は実装の検査条件と制御分岐です。条件の成立を一律に正常系とは扱いません。

| 実装箇所 | 検査条件 | 不成立時／分岐 | HTTP |
| --- | --- | --- | --- |


## 3. 正常系リソース変更

DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transactionで再認可。

参照操作も併記します。SELECTは変更ではありません。

DBへのアクセスはありません。
異常時はDB transactionがrollbackします。内容ハッシュ実体は孤立し得るため、公開認可には使いません。配送失敗はoutboxへ記録します。

## 4. 正常系レスポンス

| Status | 説明 | Media type |
| --- | --- | --- |
| 200 | Successful Response | application/json |

##### `200` Successful Response

型: `object`。定義: `{"additionalProperties": {"type": "string"}, "type": "object", "title": "Response Health"}`


**応答項目の取得元**

| 実装箇所 | 返却式（DB行・変換結果・固定値） |
| --- | --- |
| backend/src/kotorelay/operations/system/health/functions.py:8 | {'status': 'ok', 'product': 'KotoRelay'} |
| backend/src/kotorelay/operations/system/health/response_builders.py:10 | TypeAdapter(ResponseData).validate_python(value) |
| backend/src/kotorelay/operations/system/health/router.py:23 | build_response(f.build_health()) |
