"""lazunexのAPI帳票の章構成とCRUD対応を、実装由来の内容へ適用する。"""

from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path

from sqlglot import exp

REFERENCE_REVISION = "096e1e580ab1c0670c57e4febad2bd9fdd4698ee"
REFERENCE = f"https://github.com/tsuji-tomonori/lazunex/tree/{REFERENCE_REVISION}/docs/spec"
CHAPTERS = {
    "detail-design": [
        "1. 正常系入力",
        "2. 正常系前提",
        "3. 正常系リソース変更",
        "4. 正常系レスポンス",
    ],
    "interface": ["Headers", "Path Parameters", "Query Parameters", "Data", "Responses", "Samples"],
    "messages": ["API", "生成・検証方針", "メッセージ一覧", "ログ詳細", "strict検証で要求する項目"],
    "unit-test": [
        "0. Router層の暗黙処理",
        "1. 要因ごとの要素",
        "2. 直積したテストケース一覧",
        "3. テスト詳細",
    ],
    "sequence": [],
}
QUERY_SECTIONS = ["SQL種別", "SQLの概要", "利用するテーブル", "引数", "戻り値", "条件"]
LABELS = {
    "detail-design": "詳細設計",
    "interface": "インターフェース",
    "messages": "ログメッセージ",
    "query": "クエリ",
    "sequence": "シーケンス",
    "unit-test": "単体テスト詳細",
}


def sql_description(path: Path) -> str:
    """SQL正本の先頭にある、日本語一文の役割説明を取得する。"""
    lines = path.read_text().splitlines()
    description = lines[0].removeprefix("-- ").strip() if lines else ""
    if (
        not lines
        or not lines[0].startswith("-- ")
        or not re.search(r"[ぁ-んァ-ヶ一-龯]", description)
        or not description.endswith("。")
        or description.count("。") != 1
    ):
        raise ValueError(f"SQLの先頭に役割を説明する日本語一文のコメントが必要です: {path}")
    return description


def table(headers, rows):
    def cell(value):
        return str(value).replace("|", "&#124;").replace("\n", "<br>")

    return (
        "\n".join(
            "| " + " | ".join(map(cell, row)) + " |"
            for row in [headers, ["---"] * len(headers), *rows]
        )
        + "\n"
    )


def headings(body):
    """コードフェンス内の見出しに見える文字列を章と数えない。"""
    result = []
    fence = ""
    for line in body.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if not fence:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = ""
        elif not fence and (match := re.match(r"^(#{1,6}) (.+)$", line)):
            result.append((len(match[1]), match[2]))
    return result


def validate(kind, body, query_names=None):
    outline = headings(body)
    h2 = [name for level, name in outline if level == 2]
    if kind == "query":
        if query_names is not None and h2 != query_names:
            raise ValueError("query: 実装のSQL集合と章が一致しません")
        if any(not name.endswith(".sql") for name in h2) or len(h2) != len(set(h2)):
            raise ValueError("query: SQL単位の章が不正です")
        sections = [name for level, name in outline if level == 3]
        if sections != QUERY_SECTIONS * len(h2):
            raise ValueError("query: SQLの必須節に欠落・順序違いがあります")
    elif h2 != CHAPTERS[kind]:
        raise ValueError(f"{kind}: 必須章に欠落・追加・順序違いがあります: {h2}")


def sections(kind, contents):
    return "\n\n".join(
        f"## {name}\n\n{body}" for name, body in zip(CHAPTERS[kind], contents, strict=True)
    )


def resolve(node, schema):
    if "$ref" not in node:
        return node
    ref = node["$ref"]
    if not ref.startswith("#/"):
        raise ValueError(f"外部OpenAPI参照は未対応です: {ref}")
    target = schema
    for part in ref[2:].split("/"):
        target = target[part.replace("~1", "/").replace("~0", "~")]
    return {**target, **{k: v for k, v in node.items() if k != "$ref"}}


def type_name(node):
    if "$ref" in node:
        return node["$ref"].rsplit("/", 1)[-1]
    for keyword in ("anyOf", "oneOf", "allOf"):
        if keyword in node:
            return (" & " if keyword == "allOf" else " | ").join(
                type_name(n) for n in node[keyword]
            )
    if node.get("type") == "array":
        return "array<" + type_name(node.get("items", {})) + ">"
    return str(node.get("type", "object（追加項目はスキーマ参照）"))


def fields(node, schema, prefix="", seen=()):
    ref = node.get("$ref")
    if ref in seen:
        return []
    value = resolve(node, schema)
    seen = (*seen, ref) if ref else seen
    rows = []
    for name, child in value.get("properties", {}).items():
        full = f"{prefix}.{name}" if prefix else name
        prop = resolve(child, schema)
        constraints = {
            k: v
            for k, v in prop.items()
            if k not in {"title", "description", "properties", "items", "type"}
        }
        rows.append(
            [
                full,
                type_name(child),
                "必須" if name in value.get("required", []) else "任意",
                prop.get("description", "型定義に説明なし"),
                json.dumps(constraints, ensure_ascii=False),
            ]
        )
        rows.extend(fields(child, schema, full, seen))
    for keyword in ("anyOf", "oneOf", "allOf"):
        for index, child in enumerate(value.get(keyword, []), 1):
            rows.extend(fields(child, schema, f"{prefix}<{keyword}:{index}>", seen))
    if "items" in value:
        rows.extend(fields(value["items"], schema, prefix + "[]", seen))
    return rows


def schema_table(node, schema):
    rows = fields(node, schema)
    return (
        table(["項目", "型", "必須", "説明", "制約"], rows)
        if rows
        else f"型: `{type_name(node)}`。定義: `{json.dumps(node, ensure_ascii=False)}`\n"
    )


def parameters(operation, schema, location):
    return [
        resolve(p, schema)
        for p in operation.get("parameters", [])
        if resolve(p, schema).get("in") == location
    ]


def parameter_table(params):
    return (
        table(
            ["項目", "型", "必須", "説明", "制約"],
            [
                [
                    p["name"],
                    type_name(p.get("schema", {})),
                    "必須" if p.get("required") else "任意",
                    p.get("description", "OpenAPIの型制約に従う"),
                    json.dumps(p.get("schema", {}), ensure_ascii=False),
                ]
                for p in params
            ],
        )
        if params
        else "該当する入力はありません。"
    )


def input_sections(operation, schema):
    headers = parameter_table(parameters(operation, schema, "header"))
    security = operation.get("security", schema.get("security", []))
    if security:
        headers += "\n\n認証: " + json.dumps(security, ensure_ascii=False) + "\n\n"
        for requirement in security:
            for name in requirement:
                definition = schema["components"]["securitySchemes"][name]
                headers += f"`{name}`: `{json.dumps(definition, ensure_ascii=False)}`\n"
    else:
        headers += "\n\nこのoperationは認証を要求しません。"
    request = resolve(operation.get("requestBody", {}), schema)
    data = (
        "\n\n".join(
            f"媒体: `{media}`\n\n" + schema_table(value.get("schema", {}), schema)
            for media, value in request.get("content", {}).items()
        )
        or "リクエスト本文はありません。"
    )
    return [
        headers,
        parameter_table(parameters(operation, schema, "path")),
        parameter_table(parameters(operation, schema, "query")),
        data,
    ]


def response_section(operation, schema):
    rows = []
    detail = []
    for code, raw in operation.get("responses", {}).items():
        value = resolve(raw, schema)
        rows.append(
            [code, value.get("description", ""), ", ".join(value.get("content", {})) or "本文なし"]
        )
        detail.append(
            f"##### `{code}` {value.get('description', '')}\n\n"
            + "\n\n".join(
                schema_table(v.get("schema", {}), schema) for v in value.get("content", {}).values()
            )
        )
    return table(["Status", "説明", "Media type"], rows) + "\n" + "\n\n".join(detail)


def interface(operation, schema):
    samples = []
    for code, raw in operation.get("responses", {}).items():
        response = resolve(raw, schema)
        examples = {
            media: {k: v for k, v in data.items() if k in {"example", "examples"}}
            for media, data in response.get("content", {}).items()
        }
        examples = {k: v for k, v in examples.items() if v}
        if examples:
            samples.append(
                f"### HTTP {code}\n\n#### Request\n\n"
                + json.dumps(operation.get("requestBody", {}), ensure_ascii=False)
                + "\n\n#### Response\n\n```json\n"
                + json.dumps(examples, ensure_ascii=False, indent=2)
                + "\n```"
            )
    for sample in operation.get("x-test-samples", []):
        samples.append(
            f"### {sample['name']}\n\n"
            + "認証情報なしのHTTP要求と不変項目を実テストで確認します。\n\n```json\n"
            + json.dumps(sample, ensure_ascii=False, indent=2)
            + "\n```"
        )
    sample_text = "\n\n".join(samples) or (
        "このAPIのOpenAPIにHTTP応答exampleは定義されていません。"
        "架空の成功応答は生成しません。入力形式は上記のData、"
        "実際の入力と期待値は単体テスト詳細を参照してください。"
    )
    return sections(
        "interface",
        [*input_sections(operation, schema), response_section(operation, schema), sample_text],
    )


def sql_access(node):
    """DMLの変更先とSELECT/JOINの参照先を区別する。"""
    if not isinstance(node, (exp.Select, exp.Insert, exp.Update, exp.Delete)):
        raise ValueError(f"未対応CRUD: {type(node).__name__}")
    result = {}
    target = node.this.this if isinstance(node.this, exp.Schema) else node.this
    target_name = (
        target.name if isinstance(target, exp.Table) and not isinstance(node, exp.Select) else None
    )
    for item in node.find_all(exp.Table):
        result.setdefault(item.name, set())
        if item.name != target_name or any(
            item is t for s in node.find_all(exp.Select) for t in s.find_all(exp.Table)
        ):
            result[item.name].add("R")
    if target_name:
        result[target_name].add({exp.Insert: "C", exp.Update: "U", exp.Delete: "D"}[type(node)])
    return result


def csv_matrix(matrix, resources):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(["api", *resources])
    for operation, cells in sorted(matrix.items()):
        writer.writerow(
            [
                operation,
                *[
                    "".join(k for k in "CRUD" if k in cells.get(resource, set()))
                    for resource in resources
                ],
            ]
        )
    return stream.getvalue()
