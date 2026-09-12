#!/usr/bin/env python3
"""Check a target-owned as-built contract and run its local drift commands.

This validates declared coverage, not the semantic completeness of the inventory.
Commands are trusted repository code; this is not a process sandbox.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

SURFACES = {"api", "data", "infra", "frontend"}
API_DOCUMENTS = {"detail-design", "interface", "messages", "query", "sequence", "unit-test"}
HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}


def confined(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"invalid relative path: {value!r}")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"invalid relative path: {value}")
    path = root
    for part in parts:
        path /= part
        if path.is_symlink():
            raise ValueError(f"symlink is not allowed: {value}")
    if not path.resolve().is_relative_to(root):
        raise ValueError(f"path escapes repository: {value}")
    return path


def strings(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not value or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ValueError(f"{label}: expected nonempty string array")
    return value


def snapshot(root: Path, outputs: list[str]) -> dict[str, bytes]:
    result = {}
    for value in outputs:
        path = confined(root, value)
        if path.suffix.lower() != ".md" or not path.is_file():
            raise ValueError(f"missing Markdown design: {value}")
        content = path.read_bytes()
        if not content.decode("utf-8").strip():
            raise ValueError(f"empty Markdown design: {value}")
        result[value] = content
    return result


def api_outputs(root: Path, surface: dict) -> list[str]:
    """全OpenAPI operationについて6帳票の宣言漏れを拒否する。"""
    path = confined(root, surface.get("openapi"))
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or not isinstance(document.get("paths"), dict):
        raise ValueError("api: exported OpenAPI paths are required")
    ids = []
    for item in document["paths"].values():
        if not isinstance(item, dict) or "$ref" in item:
            raise ValueError("api: resolve OpenAPI path references before inventory")
        for method, operation in item.items():
            if method.lower() not in HTTP_METHODS:
                continue
            identity = operation.get("operationId") if isinstance(operation, dict) else None
            if not isinstance(identity, str) or not identity.strip():
                raise ValueError("api: every operation requires operationId")
            ids.append(identity)
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("api: empty or duplicate operation inventory")
    mapping = surface.get("operation_documents")
    if not isinstance(mapping, dict) or set(mapping) != set(ids):
        raise ValueError("api: operation_documents must exactly match OpenAPI operations")
    outputs = []
    for identity, documents in mapping.items():
        if not isinstance(documents, dict) or set(documents) != API_DOCUMENTS:
            raise ValueError(f"api {identity}: all six document kinds are required")
        paths = strings(list(documents.values()), f"api {identity}.documents")
        if len(set(paths)) != len(API_DOCUMENTS):
            raise ValueError(f"api {identity}: six distinct documents are required")
        outputs.extend(paths)
    if not set(outputs).issubset(strings(surface.get("markdown"), "api.markdown")):
        raise ValueError("api: operation documents are absent from Markdown drift inventory")
    return outputs


def check(root: Path, contract: str) -> None:
    root = root.resolve(strict=True)
    data = json.loads(confined(root, contract).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("design contract schema_version must be 1")
    surfaces = data.get("surfaces")
    if not isinstance(surfaces, dict) or not SURFACES.issubset(surfaces):
        raise ValueError("classify api, data, infra and frontend; add other surfaces as needed")
    commands = []
    outputs = []
    for name, surface in surfaces.items():
        if not isinstance(surface, dict):
            raise ValueError(f"{name}: invalid surface")
        status = surface.get("status")
        if status == "not-applicable":
            reason = surface.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                raise ValueError(f"{name}: not-applicable requires a reviewed reason")
            continue
        if status != "required":
            raise ValueError(f"{name}: incomplete design ({status!r})")
        for source in strings(surface.get("sources"), f"{name}.sources"):
            if not confined(root, source).exists():
                raise ValueError(f"{name}: missing implementation source {source}")
        if name == "api":
            api_outputs(root, surface)
        outputs.extend(strings(surface.get("markdown"), f"{name}.markdown"))
        strings(surface.get("generate"), f"{name}.generate")
        argv = strings(surface.get("check"), f"{name}.check")
        if argv not in commands:
            commands.append(argv)
    before = snapshot(root, outputs)
    for argv in commands:
        result = subprocess.run(argv, cwd=root, check=False, timeout=300)
        if result.returncode:
            raise ValueError(f"design drift command failed ({result.returncode}): {argv}")
        if snapshot(root, outputs) != before:
            raise ValueError(f"check command rewrote generated Markdown: {argv}")
    print(f"as-built check passed: {len(commands)} commands, {len(before)} Markdown files")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--contract", default=".dev-standard/design.json")
    args = parser.parse_args()
    try:
        check(args.root, args.contract)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"as-built incomplete: {exc}\n")


if __name__ == "__main__":
    main()
