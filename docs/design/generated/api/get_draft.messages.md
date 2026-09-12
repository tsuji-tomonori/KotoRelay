<!-- 実装から生成。直接編集しない。入力SHA256: 209f2912c47883d8fdc722aafdde6cf403dff105c2efced6770337a06a320dd2 -->

# 下書きを取得 — messages

| ID | level | テンプレート | 条件 | 出力型・マスク | 場所 | 運用 |
| --- | --- | --- | --- | --- | --- | --- |
| KR_REQUEST | INFO | request_id=%s method=%s status=%s | HTTP応答生成時 | request_id:UUID、method:str、status:int。機密本文とJWTは記録しない。 | backend/src/kotorelay/main.py:security_headers | 5xxはrequest_idから処理失敗を照合。409は再読込後に再試行。 |
