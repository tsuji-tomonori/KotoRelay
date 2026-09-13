"""systemのhealthの業務判定と処理を実行する。"""

from __future__ import annotations


def build_health() -> dict[str, str]:
    """後続処理に渡すデータを組み立てる。"""
    return {"status": "ok", "product": "KotoRelay"}
