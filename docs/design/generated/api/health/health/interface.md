<!-- 実装から生成。直接編集しない。入力SHA256: a4642be092686b22c6cb0bbcfdd011c0a0c93352fc1191e08d5c7dfccac4e973 -->

# 死活確認 — インターフェース

章構成: [lazunex API帳票](https://github.com/tsuji-tomonori/lazunex/tree/096e1e580ab1c0670c57e4febad2bd9fdd4698ee/docs/spec/40.apis)。

## Headers

該当する入力はありません。

このoperationは認証を要求しません。

## Path Parameters

該当する入力はありません。

## Query Parameters

該当する入力はありません。

## Data

リクエスト本文はありません。

## Responses

| Status | 説明 | Media type |
| --- | --- | --- |
| 200 | Successful Response | application/json |

##### `200` Successful Response

型: `object`。定義: `{"additionalProperties": {"type": "string"}, "type": "object", "title": "Response Health"}`


## Samples

### 死活確認の成功

認証情報なしのHTTP要求と不変項目を実テストで確認します。

```json
{
  "name": "死活確認の成功",
  "method": "GET",
  "path": "/api/health",
  "expected_status": 200,
  "expected_fields": {
    "status": "ok",
    "product": "KotoRelay"
  }
}
```