"""FastAPIの構成と機密を除いたエラー応答を定義する。"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from uuid import uuid4

import psycopg
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from kotorelay.config import Settings
from kotorelay.errors import Problem
from kotorelay.operations.chat.router import router as chat
from kotorelay.operations.documents.router import router as documents
from kotorelay.operations.groups.router import router as groups
from kotorelay.operations.images.router import router as images
from kotorelay.operations.indexing.router import router as indexing
from kotorelay.operations.metrics.router import router as metrics
from kotorelay.operations.reviews.router import router as reviews
from kotorelay.operations.system.router import router as system
from kotorelay.runtime import Runtime

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("kotorelay")
logger.setLevel(logging.INFO)
LOG_MESSAGES = {"KR_REQUEST": "request_id=%s method=%s status=%s"}


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()
    app = FastAPI(title="KotoRelay API", version="0.1.0")
    app.state.runtime = Runtime(config)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[config.frontend_origin],
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
    )
    for router in [system, documents, reviews, images, groups, metrics, indexing, chat]:
        app.include_router(router)

    @app.middleware("http")
    async def security_headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request.state.request_id = str(uuid4())
        response = await call_next(request)
        response.headers.update(
            {
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "no-referrer",
                "X-Request-ID": request.state.request_id,
            }
        )
        logger.info(
            LOG_MESSAGES["KR_REQUEST"],
            request.state.request_id,
            request.method,
            response.status_code,
        )
        return response

    @app.exception_handler(Problem)
    async def problem(request: Request, exc: Problem) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status,
            content={
                "code": exc.code,
                "message": exc.message,
                "request_id": request.state.request_id,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "code": "invalid_input",
                "message": "入力形式を確認してください。",
                "request_id": request.state.request_id,
            },
        )

    @app.exception_handler(psycopg.Error)
    async def database_error(request: Request, exc: psycopg.Error) -> JSONResponse:
        conflict = exc.sqlstate in {"40001", "23505", "OC000", "OC001"}
        return JSONResponse(
            status_code=409 if conflict else 503,
            content={
                "code": "conflict" if conflict else "unavailable",
                "message": "競合しました。再読込してください。"
                if conflict
                else "一時的に利用できません。",
                "request_id": request.state.request_id,
            },
        )

    return app


app = create_app()
