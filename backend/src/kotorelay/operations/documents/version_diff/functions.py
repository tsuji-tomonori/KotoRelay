"""documentsのversion_diffの業務判定と処理を実行する。"""

from __future__ import annotations

import difflib

from kotorelay.context import Context


def diff(ctx: Context, document_id: str, left: str, right: str) -> dict[str, str]:
    doc = ctx.document(document_id, "draft")
    a, b = ctx.version(doc, left), ctx.version(doc, right)
    lines = difflib.unified_diff(
        ctx.objects.get(a.body_key).decode().splitlines(),
        ctx.objects.get(b.body_key).decode().splitlines(),
        fromfile=left,
        tofile=right,
        lineterm="",
    )
    return {"left": left, "right": right, "diff": "\n".join(lines)}
