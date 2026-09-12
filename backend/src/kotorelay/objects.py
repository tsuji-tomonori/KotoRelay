"""本文・画像・OCRの実体を非公開の内容アドレスへ保存する。"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Protocol

import boto3
from botocore.config import Config

from kotorelay.config import Settings
from kotorelay.errors import require


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Objects(Protocol):
    def put(self, data: bytes, media_type: str = "application/octet-stream") -> str: ...
    def get(self, key: str, expected_hash: str | None = None) -> bytes: ...
    def delete(self, key: str) -> None: ...


class LocalObjects:
    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, key: str) -> Path:
        require(len(key) == 64 and all(c in "0123456789abcdef" for c in key), "integrity", 503)
        return self.root / key

    def put(self, data: bytes, media_type: str = "application/octet-stream") -> str:
        key = digest(data)
        self.path(key).write_bytes(data)
        return key

    def get(self, key: str, expected_hash: str | None = None) -> bytes:
        path = self.path(key)
        require(path.is_file(), "integrity", 503)
        value = path.read_bytes()
        require(digest(value) == (expected_hash or key), "integrity", 503)
        return value

    def delete(self, key: str) -> None:
        self.path(key).unlink(missing_ok=True)


class S3Objects:
    def __init__(self, settings: Settings):
        self.bucket = settings.bucket
        self.prefix = settings.organization_id + "/"
        self.client = boto3.client(
            "s3",
            region_name=settings.region,
            config=Config(
                connect_timeout=3,
                read_timeout=10,
                retries={"total_max_attempts": 2, "mode": "adaptive"},
            ),
        )

    def put(self, data: bytes, media_type: str = "application/octet-stream") -> str:
        key = digest(data)
        self.client.put_object(
            Bucket=self.bucket,
            Key=self.prefix + key,
            Body=data,
            ContentType=media_type,
            ServerSideEncryption="AES256",
        )
        return key

    def get(self, key: str, expected_hash: str | None = None) -> bytes:
        with self.client.get_object(Bucket=self.bucket, Key=self.prefix + key)["Body"] as body:
            value = body.read()
        require(digest(value) == (expected_hash or key), "integrity", 503)
        return value

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=self.prefix + key)
