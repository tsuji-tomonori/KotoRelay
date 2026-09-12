<!-- 実装から生成。直接編集しない。入力SHA256: f4209c4ed7b292c6ed57aa300cf25000f8931a1f59b1fb43cfeb436b1d949dbe -->

# 認可されたOCR領域を取得 — messages

| ID | level | テンプレート | 条件 | 出力型・マスク | 場所 | 運用 |
| --- | --- | --- | --- | --- | --- | --- |
| KR_REQUEST | INFO | request_id=%s method=%s status=%s | HTTP応答生成時 | request_id:UUID、method:str、status:int。機密本文とJWTは記録しない。 | backend/src/kotorelay/main.py:security_headers | 5xxはrequest_idから処理失敗を照合。409は再読込後に再試行。 |
