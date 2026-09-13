"""indexingのretry_jobの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context
from kotorelay.engines import Engine
from kotorelay.generated import models
from kotorelay.operations.indexing.shared.functions import process


def retry(ctx: Context, engine: Engine, job_id: str) -> models.OutboxRow:
    """運用権限と現行状態を確認して共有のジョブ配送処理を再実行する。"""
    return process(ctx, engine, job_id)
