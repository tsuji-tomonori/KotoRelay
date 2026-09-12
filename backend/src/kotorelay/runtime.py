"""認証と依存先の生成をAPIの業務処理から分離する。"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Annotated

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from kotorelay.config import Settings
from kotorelay.context import Context
from kotorelay.db import Database
from kotorelay.engines import BedrockEngine, Engine, LocalEngine
from kotorelay.errors import Problem, require
from kotorelay.objects import LocalObjects, Objects, S3Objects

bearer = HTTPBearer(auto_error=False)


class Runtime:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.objects: Objects = (
            S3Objects(settings) if settings.mode == "aws" else LocalObjects(settings.object_root)
        )
        self.engine: Engine = BedrockEngine(settings) if settings.mode == "aws" else LocalEngine()
        self.jwks = (
            jwt.PyJWKClient(settings.issuer + "/.well-known/jwks.json")
            if settings.mode == "aws"
            else None
        )

    def authenticate(self, token: str) -> str:
        if self.settings.mode == "local":
            require(
                token
                in {
                    "demo-author",
                    "demo-reviewer",
                    "demo-reader",
                    "demo-leader",
                    "demo-operator",
                    "demo-other",
                },
                "unauthenticated",
                401,
            )
            return token
        require(
            self.jwks is not None and self.settings.issuer.startswith("https://"),
            "unauthenticated",
            401,
        )
        try:
            if self.jwks is None:
                raise jwt.InvalidTokenError()
            signing_key = self.jwks.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=self.settings.issuer,
                options={"verify_aud": False, "require": ["exp", "iat", "sub", "iss"]},
            )
            require(
                claims.get("token_use") == "access"
                and claims.get("client_id") == self.settings.client_id,
                "unauthenticated",
                401,
            )
            require(isinstance(claims["sub"], str), "unauthenticated", 401)
            return str(claims["sub"])
        except (jwt.PyJWTError, jwt.PyJWKClientError) as exc:
            raise Problem(401, "unauthenticated", "ログインが必要です。") from exc

    @contextmanager
    def context(self, subject: str) -> Iterator[Context]:
        with Database(self.settings).transaction() as db:
            yield Context(db, self.settings, self.objects, subject)


def runtime(request: Request) -> Runtime:
    result: Runtime = request.app.state.runtime
    return result


def subject(
    rt: Annotated[Runtime, Depends(runtime)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> str:
    require(credentials is not None, "unauthenticated", 401)
    return rt.authenticate(credentials.credentials if credentials else "")


def context(
    rt: Annotated[Runtime, Depends(runtime)], user: Annotated[str, Depends(subject)]
) -> Iterator[Context]:
    with rt.context(user) as ctx:
        yield ctx


Ctx = Annotated[Context, Depends(context)]
Rt = Annotated[Runtime, Depends(runtime)]
Subject = Annotated[str, Depends(subject)]
