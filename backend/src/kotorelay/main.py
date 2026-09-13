"""FastAPIの構成と機密を除いたエラー応答を定義する。"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from uuid import UUID, uuid4

import psycopg
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from kotorelay.config import Settings
from kotorelay.error_responses import (
    INVALID_INPUT,
    UNAVAILABLE,
    ErrorOutcome,
    database_outcome,
    problem_outcome,
)
from kotorelay.errors import Problem
from kotorelay.operational_logging import REQUEST_ID, MessageId, OperationalLogContext, ops_logger
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
        token = REQUEST_ID.set(UUID(request.state.request_id))
        try:
            response = await call_next(request)
        finally:
            REQUEST_ID.reset(token)
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

    def error_response(request: Request, exc: Exception, outcome: ErrorOutcome) -> JSONResponse:
        context = OperationalLogContext(
            request_id=UUID(request.state.request_id),
            exception_type=type(exc).__name__,
            status=outcome.status,
            code=outcome.code,
            message=outcome.message,
        )
        if outcome.status >= 500:
            ops_logger.error(MessageId.HTTP_FAILED, context_model=context)
        else:
            ops_logger.warning(MessageId.HTTP_REJECTED, context_model=context)
        return JSONResponse(
            status_code=outcome.status,
            content={
                "code": outcome.code,
                "message": outcome.message,
                "request_id": request.state.request_id,
            },
        )

    @app.exception_handler(Problem)
    async def problem(request: Request, exc: Problem) -> JSONResponse:
        return error_response(request, exc, problem_outcome(exc))

    @app.exception_handler(RequestValidationError)
    async def validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        return error_response(request, exc, INVALID_INPUT)

    @app.exception_handler(psycopg.Error)
    async def database_error(request: Request, exc: psycopg.Error) -> JSONResponse:
        return error_response(request, exc, database_outcome(exc))

    async def external_error(request: Request, exc: Exception) -> JSONResponse:
        return error_response(request, exc, UNAVAILABLE)

    for exception_type in (BotoCoreError, ClientError, OSError, TimeoutError):
        app.add_exception_handler(exception_type, external_error)

    return app


app = create_app()
