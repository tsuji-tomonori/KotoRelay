"""API操作の契約と、実HTTP試験で確認するサンプルを定義する。"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


@dataclass(frozen=True)
class ApiContract:
    """APIの識別・HTTP境界・設計の配置を一つの操作へ対応付ける。"""

    operation_id: str
    group: str
    method: str
    path: str
    summary: str
    auth_mode: Literal["public", "bearer"]

    def openapi_extra(self, samples: tuple[ApiSample, ...]) -> dict[str, object]:
        """実装の所有先と認証境界をOpenAPIと生成設計へ公開する。"""
        return {
            "x-api-package": f"operations/{self.group}/{self.operation_id}",
            "x-auth-mode": self.auth_mode,
            "x-test-samples": [asdict(sample) for sample in samples],
        }


@dataclass(frozen=True)
class ApiSample:
    """HTTPで再現する入力と、応答の検証対象項目を保持する。"""

    name: str
    method: str
    path: str
    expected_status: int
    expected_fields: dict[str, object]
