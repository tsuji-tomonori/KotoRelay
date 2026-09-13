"""documentsのversion_diffの業務判定と処理を実行する。"""

from __future__ import annotations

import difflib
import uuid

import kotorelay.context as context_types
import kotorelay.generated.models as models


def document_doc(ctx: context_types.Context, document_id: uuid.UUID) -> models.DocumentsRow:
    """文書を取得して要求された操作の権限を確認する。"""
    return ctx.document(str(document_id), "draft")


def load_left_version(
    doc: models.DocumentsRow, ctx: context_types.Context, left: uuid.UUID
) -> models.VersionsRow:
    """対象文書に属する確定版を取得する。"""
    return ctx.version(doc, str(left))


def load_right_version(
    doc: models.DocumentsRow, ctx: context_types.Context, right: uuid.UUID
) -> models.VersionsRow:
    """対象文書に属する確定版を取得する。"""
    return ctx.version(doc, str(right))


def load_left_lines(a: models.VersionsRow, ctx: context_types.Context) -> list[str]:
    """版の本文を比較用の行へ分割する。"""
    return ctx.objects.get(a.body_key).decode().splitlines()


def load_right_lines(b: models.VersionsRow, ctx: context_types.Context) -> list[str]:
    """版の本文を比較用の行へ分割する。"""
    return ctx.objects.get(b.body_key).decode().splitlines()


def build_version_diff(left: uuid.UUID, right: uuid.UUID, lines: list[str]) -> dict[str, str]:
    """後続処理に渡すデータを組み立てる。"""
    return {"left": str(left), "right": str(right), "diff": "\n".join(lines)}


def compare_bodies(
    left_lines: list[str], right_lines: list[str], left: str, right: str
) -> list[str]:
    """二つの版の本文から統一差分形式の変更行を生成する。"""
    return list(
        difflib.unified_diff(left_lines, right_lines, fromfile=left, tofile=right, lineterm="")
    )
