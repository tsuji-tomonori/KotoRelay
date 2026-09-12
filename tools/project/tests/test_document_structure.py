"""参照帳票の章契約、API階層、CRUDの実装対応が退行しないことを確認する。"""

import csv
import importlib.util
import io
import json
from pathlib import Path

import pytest
import sqlglot


def module(name):
    path = Path("tools/project") / (name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


@pytest.fixture(scope="module")
def generated():
    return module("design").build()[0]


def test_全APIがグループとAPIの下で6帳票を持ち索引から辿れる(generated):
    manifest = json.loads(generated["manifest.json"])
    assert len(manifest["operation_documents"]) == 26
    for operation, documents in manifest["operation_documents"].items():
        assert set(documents) == {
            "detail-design",
            "interface",
            "messages",
            "query",
            "sequence",
            "unit-test",
        }
        for kind, path in documents.items():
            relative = path.removeprefix("docs/design/generated/")
            parts = relative.split("/")
            assert len(parts) == 4 and parts[0] == "api"
            assert parts[2] == operation and parts[3] == kind + ".md"
            module("api_documents").validate(kind, generated[relative])
            assert f"({kind}.md)" in generated[f"api/{parts[1]}/{operation}/README.md"]
            assert f"({operation}/README.md)" in generated[f"api/{parts[1]}/README.md"]


@pytest.mark.parametrize("change", ["欠落", "逆順", "重複"])
def test_詳細設計の章の欠落と順序変更と重複を拒否する(change):
    headings = ["1. 正常系入力", "2. 正常系前提", "3. 正常系リソース変更", "4. 正常系レスポンス"]
    original = "\n".join("## " + h + "\n内容" for h in headings)
    layout = module("api_documents")
    layout.validate("detail-design", original)
    changed = (
        headings[1:]
        if change == "欠落"
        else list(reversed(headings))
        if change == "逆順"
        else headings + headings[:1]
    )
    with pytest.raises(ValueError, match="必須章"):
        layout.validate("detail-design", "\n".join("## " + h for h in changed))


def test_コード内の見出しを章と数えずSQLごとの必須節を確認する():
    layout = module("api_documents")
    query = "## read.sql\n" + "\n".join(
        "### " + h + "\n内容"
        for h in ["SQL種別", "SQLの概要", "利用するテーブル", "引数", "戻り値", "条件"]
    )
    with pytest.raises(ValueError, match="SQL集合"):
        layout.validate("query", "DB操作はありません。", ["read.sql"])
    layout.validate("query", query + "\n```sql\n## 偽の見出し\n```")
    with pytest.raises(ValueError, match="必須節"):
        layout.validate("query", query.replace("### 引数\n内容", ""))


@pytest.mark.parametrize(
    ("statement", "expected"),
    [
        ("SELECT a.id FROM a JOIN b ON a.id = b.id", {"a": {"R"}, "b": {"R"}}),
        ("INSERT INTO a (id) SELECT id FROM b", {"a": {"C"}, "b": {"R"}}),
        ("UPDATE a SET name = :name WHERE id = :id", {"a": {"U"}}),
        ("DELETE FROM a WHERE id = :id", {"a": {"D"}}),
    ],
)
def test_SQLの変更先と参照先を区別してCRUDを生成する(statement, expected):
    assert module("api_documents").sql_access(sqlglot.parse_one(statement)) == expected


def test_実装にあるDBと保存先だけを全APIのCRUD表に出す(generated):
    tables = {}
    for kind in ["db", "objects", "vectors"]:
        tables[kind] = {
            row["api"]: row for row in csv.DictReader(io.StringIO(generated[f"crud/{kind}.csv"]))
        }
        assert len(tables[kind]) == 26
        assert all(not value for key, value in tables[kind]["health"].items() if key != "api")
    assert tables["db"]["create_document"]["documents"] == "C"
    assert tables["db"]["get_identity"]["memberships"] == "R"
    assert tables["objects"]["create_document"]["content_object"] == "CU"
    assert tables["vectors"]["ask_question"]["vector"] == "R"
    assert "抽出根拠" in generated["crud/db.md"]
    assert "```mermaid" in generated["crud/db.md"]
    assert not any(path.startswith("api/") and len(path.split("/")) == 2 for path in generated)


def test_OpenAPIの参照型と配列と認証を人向けの章へ展開する():
    layout = module("api_documents")
    schema = {
        "components": {
            "schemas": {
                "Body": {
                    "type": "object",
                    "required": ["names"],
                    "properties": {"names": {"type": "array", "items": {"type": "string"}}},
                }
            },
            "securitySchemes": {"Bearer": {"type": "http", "scheme": "bearer"}},
        }
    }
    operation = {
        "security": [{"Bearer": []}],
        "requestBody": {
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Body"}}}
        },
        "responses": {
            "200": {
                "description": "成功",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Body"}}},
            }
        },
    }
    rendered = layout.interface(operation, schema)
    assert "names" in rendered and "array<string>" in rendered and "bearer" in rendered
    assert [h for level, h in layout.headings(rendered) if level == 2] == [
        "Headers",
        "Path Parameters",
        "Query Parameters",
        "Data",
        "Responses",
        "Samples",
    ]
    assert "架空の成功応答は生成しません" in rendered
