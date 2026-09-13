"""systemのhealthの業務判定と処理を実行する。"""

from __future__ import annotations


def health() -> dict[str, str]:
    """外部依存へ接続せずプロセスの稼働状態を返す。"""
    return {"status": "ok", "product": "KotoRelay"}
