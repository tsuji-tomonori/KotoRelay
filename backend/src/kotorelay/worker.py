"""outboxを小さいtransactionで配送し、中断した処理を再開する。"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from kotorelay.config import Settings
from kotorelay.generated import queries as q
from kotorelay.operations.indexing.functions import process
from kotorelay.runtime import Runtime

if TYPE_CHECKING:
    from collections.abc import Mapping


def run_once(runtime: Runtime) -> int:
    subject = (
        "demo-operator" if runtime.settings.mode == "local" else runtime.settings.worker_subject
    )
    with runtime.context(subject) as ctx:
        pending = [
            j.id
            for j in q.outbox_list(ctx.db, ctx.org)
            if j.status in {"pending", "failed", "retained"} and j.attempts < 5
        ][:10]
    for job_id in pending:
        with runtime.context(subject) as ctx:
            process(ctx, runtime.engine, job_id)
    return len(pending)


def handler(event: Mapping[str, object], context: object) -> dict[str, int]:
    return {"processed": run_once(Runtime(Settings()))}


def main() -> None:
    runtime = Runtime(Settings())
    while True:
        run_once(runtime)
        time.sleep(5)


if __name__ == "__main__":
    main()
