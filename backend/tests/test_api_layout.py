"""API単位の契約と実サンプルが実装に接続されていることを確認する。"""

import importlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "src/kotorelay"
PACKAGES = sorted(
    "kotorelay." + ".".join(path.parent.relative_to(ROOT).parts)
    for path in ROOT.glob("operations/*/*/contract.py")
)


@pytest.mark.parametrize("package", PACKAGES, ids=[p.split(".")[-1] for p in PACKAGES])
def test_APIごとのサンプルを実HTTPで再現する(client, package):
    contract = importlib.import_module(package + ".contract").CONTRACT
    for sample in importlib.import_module(package + ".samples").SAMPLES:
        response = client.request(sample.method, sample.path)
        assert response.status_code == sample.expected_status
        assert all(response.json()[key] == value for key, value in sample.expected_fields.items())
        operation = client.app.openapi()["paths"][contract.path][contract.method.lower()]
        assert operation["operationId"] == contract.operation_id
        assert operation["x-auth-mode"] == contract.auth_mode
        assert operation["x-test-samples"][0]["expected_status"] == sample.expected_status
        assert "X-Request-ID" in response.headers
