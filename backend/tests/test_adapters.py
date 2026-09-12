"""DB・AWS SDK・OCR・認証境界の正常・例外を単体試験する。"""

from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

import jwt
import psycopg
import pytest
from botocore.response import StreamingBody
from kotorelay.db import Database
from kotorelay.engines import BedrockEngine, LocalEngine, terms
from kotorelay.errors import Problem
from kotorelay.generated import queries as q
from kotorelay.objects import LocalObjects, S3Objects
from kotorelay.operations.images.functions import normalize_image, run_ocr
from kotorelay.operations.indexing.functions import split_chunks
from kotorelay.runtime import Runtime
from PIL import Image


def stream(data: bytes):
    return StreamingBody(io.BytesIO(data), len(data))


def test_S3のハッシュ照合とストリーム解放(settings):
    client = MagicMock()
    with patch("kotorelay.objects.boto3.client", return_value=client):
        objects = S3Objects(settings)
    value = b"content"
    key = objects.put(value, "text/plain")
    body = stream(value)
    client.get_object.return_value = {"Body": body}
    assert objects.get(key) == value
    assert body._raw_stream.closed
    client.put_object.assert_called_once_with(
        Bucket="",
        Key=settings.organization_id + "/" + key,
        Body=value,
        ContentType="text/plain",
        ServerSideEncryption="AES256",
    )
    objects.delete(key)
    client.delete_object.assert_called_once()
    client.get_object.return_value = {"Body": stream(b"corrupted")}
    with pytest.raises(Problem):
        objects.get(key)


def test_ローカル実体の改変とパス逸脱を拒否する(tmp_path):
    objects = LocalObjects(str(tmp_path))
    key = objects.put(b"test")
    assert objects.get(key) == b"test"
    objects.delete(key)
    objects.delete(key)
    with pytest.raises(Problem):
        objects.get(key)
    for invalid in ["../secret", "z" * 64, ""]:
        with pytest.raises(Problem):
            objects.get(invalid)
    key = objects.put(b"ok")
    (tmp_path / key).write_bytes(b"bad")
    with pytest.raises(Problem):
        objects.get(key)


def test_Bedrockへ構造化画像bytesと出力上限を渡す(settings):
    client = MagicMock()
    vectors = MagicMock()
    with patch("kotorelay.engines.boto3.client", side_effect=[client, vectors]):
        engine = BedrockEngine(settings)
    client.converse.return_value = {
        "output": {"message": {"content": [{"text": "回答"}, {"text": "続き"}, {"toolUse": {}}]}}
    }
    assert engine.generate("質問", ["根拠"], [b"png"]) == "回答\n続き"
    args = client.converse.call_args.kwargs
    assert args["messages"][0]["content"][1]["image"]["source"]["bytes"] == b"png"
    assert args["inferenceConfig"]["maxTokens"] == 1000
    assert "toolConfig" not in args


def test_ベクトル検索の前に組織と文書フィルタを設定する(settings):
    client = MagicMock()
    vectors = MagicMock()
    with patch("kotorelay.engines.boto3.client", side_effect=[client, vectors]):
        engine = BedrockEngine(settings)
    client.invoke_model.side_effect = lambda **_: {"body": stream(b'{"embedding":[0.1,0.2]}')}
    engine.index("chunk", "本文", "doc", "version")
    assert (
        vectors.put_vectors.call_args.kwargs["vectors"][0]["metadata"]["organization_id"]
        == settings.organization_id
    )
    assert engine.search("質問", []) == []
    vectors.query_vectors.return_value = {"vectors": [{"key": "chunk", "distance": 0.1}]}
    assert engine.search("質問", [str(i) for i in range(101)]) == ["chunk", "chunk"]
    assert vectors.query_vectors.call_count == 2
    assert "indexArn" in vectors.query_vectors.call_args.kwargs
    assert "vectorBucketName" not in vectors.query_vectors.call_args.kwargs
    assert "indexArn" in vectors.put_vectors.call_args.kwargs
    assert (
        vectors.query_vectors.call_args.kwargs["filter"]["$and"][0]["organization_id"]["$eq"]
        == settings.organization_id
    )
    engine.delete([str(i) for i in range(101)])
    assert vectors.delete_vectors.call_count == 2


def test_ローカル抽出はモデル名で区別する():
    engine = LocalEngine()
    assert engine.search("質問", []) is None
    assert engine.index("a", "本文", "d", "v") is None
    assert engine.delete(["a"]) is None
    assert "ローカル検索" in engine.generate("質問", ["本文"], [])
    assert terms("") == set() and "開発" in terms("開発手順")


def test_OCRの座標と読み順を正規化する():
    result = MagicMock(
        stdout=b"left\ttop\twidth\theight\tconf\ttext\n10\t20\t30\t40\t90\tHello\n0\t0\t0\t0\t-1\t\n"
    )
    with patch("kotorelay.operations.images.functions.subprocess.run", return_value=result):
        ocr = run_ocr(b"png", 100, 200, "tesseract")
    assert ocr.status == "ready" and ocr.regions[0].x == 0.1 and ocr.regions[0].y == 0.1
    assert ocr.regions[0].confidence == 0.9 and ocr.regions[0].order == 0
    with patch(
        "kotorelay.operations.images.functions.subprocess.run",
        return_value=MagicMock(stdout=b"left\ttop\twidth\theight\tconf\ttext\n"),
    ):
        assert run_ocr(b"png", 1, 1, "tesseract").regions == []


def test_画像の解像度と正規化後サイズを制限する():
    output = io.BytesIO()
    Image.new("RGB", (30, 30), "white").save(output, format="JPEG")
    data = output.getvalue()
    value, width, height = normalize_image(data, 5000, 1000)
    assert value.startswith(b"\x89PNG") and (width, height) == (30, 30)
    with pytest.raises(Problem):
        normalize_image(data, 5000, 10)
    with pytest.raises(Problem):
        normalize_image(data, 1, 1000)
    with patch("kotorelay.operations.images.functions.Image.open", side_effect=OSError("bad")):
        with pytest.raises(Problem):
            normalize_image(b"x", 5000, 1000)


def test_見出しと長文を上限内のチャンクへ分割する():
    assert split_chunks("") == []
    chunks = split_chunks("# 見出し\n" + ("あ" * 3000) + "\n# 次\n本文")
    assert all(len(text) <= 1200 for _, text in chunks)
    assert chunks[-1][0] == "次" and "本文" in chunks[-1][1]
    assert len(split_chunks("行\n" * 1500)) >= 3


def test_DBポートのparameter_bindingとtransaction終了を検証する(settings):
    connection = MagicMock()
    connection.__enter__.return_value = connection
    connection.execute.return_value.fetchall.return_value = [
        {"id": "1", "organization_id": "1", "name": "組織", "revision": 1, "suspended": False}
    ]
    connection.execute.return_value.rowcount = 1
    db = Database(settings)
    with patch("kotorelay.db.psycopg.connect", return_value=connection):
        with db.transaction():
            assert q.organizations_get(db, "1", "1")[0].name == "組織"
            assert (
                q.organizations_fence(
                    db,
                    q.OrganizationsRow(
                        id="1", organization_id="1", name="組織", revision=1, suspended=False
                    ),
                )
                == 1
            )
        assert db.connection is None
    assert connection.isolation_level == psycopg.IsolationLevel.REPEATABLE_READ
    with pytest.raises(RuntimeError):
        q.organizations_get(db, "1", "1")
    with pytest.raises(RuntimeError):
        db.execute("unused", {})


def test_DSQLは公式コネクタとTLS検証を使う(settings):
    db = Database(
        settings.model_copy(
            update={"mode": "aws", "dsql_host": "example.dsql.ap-northeast-1.on.aws"}
        )
    )
    with patch("aurora_dsql_psycopg.connect", return_value=MagicMock()) as connect:
        db.connect()
    assert connect.call_args.kwargs["sslmode"] == "verify-full"
    assert connect.call_args.kwargs["user"] == "kotorelay_app"


def test_本番認証ではローカルトークンを受け付けない(settings):
    runtime = Runtime(settings)
    runtime.settings = settings.model_copy(
        update={"mode": "aws", "issuer": "https://issuer", "client_id": "client"}
    )
    runtime.jwks = MagicMock()
    with patch(
        "kotorelay.runtime.jwt.decode",
        return_value={"sub": "subject", "token_use": "access", "client_id": "client"},
    ):
        assert runtime.authenticate("jwt") == "subject"
    with patch("kotorelay.runtime.jwt.decode", side_effect=jwt.InvalidTokenError("expired")):
        with pytest.raises(Problem):
            runtime.authenticate("demo-author")
    with patch(
        "kotorelay.runtime.jwt.decode",
        return_value={"sub": "subject", "token_use": "id", "client_id": "client"},
    ):
        with pytest.raises(Problem):
            runtime.authenticate("jwt")


def test_Lambdaエントリポイントを構成する():
    from kotorelay.handler import handler

    assert callable(handler)


def test_移行は各DDLを独立実行する(settings, tmp_path, monkeypatch):
    from kotorelay.migrate import main

    (tmp_path / "001.sql").write_text("CREATE TABLE first (id integer);")
    (tmp_path / "002.sql").write_text("CREATE TABLE second (id integer);")
    connection = MagicMock()
    connection.__enter__.return_value = connection
    monkeypatch.setattr("sys.argv", ["migrate", "--directory", str(tmp_path)])
    with patch("kotorelay.migrate.Database.connect", return_value=connection):
        main()
    assert connection.autocommit is True
    assert connection.execute.call_count == 2


def test_ベクトルの全件読戻しで部分保存を検知する(settings):
    client = MagicMock()
    vectors = MagicMock()
    with patch("kotorelay.engines.boto3.client", side_effect=[client, vectors]):
        engine = BedrockEngine(settings)
    vectors.get_vectors.side_effect = lambda **kw: {"vectors": [{"key": k} for k in kw["keys"]]}
    assert engine.verify([str(i) for i in range(101)])
    assert vectors.get_vectors.call_count == 2
    vectors.get_vectors.side_effect = None
    vectors.get_vectors.return_value = {"vectors": []}
    assert not engine.verify(["missing"])
    assert engine.verify([])


def test_workerのLambda入口とローカルループを実行する(settings):
    from kotorelay import worker

    with patch.object(worker, "Runtime"), patch.object(worker, "run_once", return_value=2):
        assert worker.handler({}, None) == {"processed": 2}
        with patch.object(worker.time, "sleep", side_effect=KeyboardInterrupt):
            with pytest.raises(KeyboardInterrupt):
                worker.main()


def test_モデルへ送信できない画像寸法を受付時に拒否する():
    value = io.BytesIO()
    Image.new("RGB", (8001, 1), "white").save(value, format="PNG")
    with pytest.raises(Problem):
        normalize_image(value.getvalue(), 3 * 1024 * 1024, 20_000_000)
