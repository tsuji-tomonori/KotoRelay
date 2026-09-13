"""型付きの運用ログに例外分類・安全な応答・運用手順を必須で記録する。"""

from __future__ import annotations

import json
import logging
from contextvars import ContextVar
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from kotorelay.errors import Problem


class MessageId(StrEnum):
    HTTP_REJECTED = "KR_HTTP_REJECTED"
    HTTP_FAILED = "KR_HTTP_FAILED"
    MODEL_FAILED = "KR_MODEL_FAILED"
    INDEX_FAILED = "KR_INDEX_FAILED"
    OCR_FAILED = "KR_OCR_FAILED"
    EVIDENCE_REJECTED = "KR_EVIDENCE_REJECTED"


class OperationalMessage(BaseModel):
    """生成帳票と実行時に共有するログ定義。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    level: Literal["WARNING", "ERROR"]
    summary: str
    when: str
    response: str
    check_procedure: str
    remediation_procedure: str


CATALOG = {
    MessageId.HTTP_REJECTED: OperationalMessage(
        level="WARNING",
        summary="業務条件または入力検証によりリクエストを拒否しました。",
        when="Problemの4xx、RequestValidationError、DBの競合例外をHTTP境界で捕捉した場合。",
        response="HTTP status / code / messageはcontextの応答と一致。request_idは相関ID。",
        check_procedure="request_idで検索し、例外型・code・HTTP statusを確認する。",
        remediation_procedure="401は再認証、403/404は権限、409は再読込、422は入力、429は時間を置いて再試行する。",
    ),
    MessageId.HTTP_FAILED: OperationalMessage(
        level="ERROR",
        summary="処理を完了できずエラー応答を返しました。",
        when="Problemの5xx、競合以外のpsycopg.Error、外部サービス例外をHTTP境界で捕捉した場合。",
        response="HTTP status / code / messageはcontextの応答と一致。request_idは相関ID。",
        check_procedure="request_idから例外型と応答コードを調べ、DB接続・実体整合性・外部サービス稼働を確認する。",
        remediation_procedure="依存先を復旧し、保存済み状態を確認して同じ操作IDで再試行する。",
    ),
    MessageId.MODEL_FAILED: OperationalMessage(
        level="ERROR",
        summary="回答モデルの呼出しが失敗しました。",
        when="回答生成中にBotoCoreError / ClientError / TimeoutErrorを捕捉した場合。",
        response=(
            "後続の再認可と保存が成功すればHTTP 200、AnswerView.status=failed、"
            "answer=現在利用できる根拠が不足しているため、回答を保留しました。"
        ),
        check_procedure="request_idと例外型からモデルの稼働と呼出し権限を確認する。",
        remediation_procedure="依存先の復旧後に新しい質問として再実行する。",
    ),
    MessageId.INDEX_FAILED: OperationalMessage(
        level="ERROR",
        summary="索引または削除ジョブの実行が失敗しました。",
        when="ジョブ実行中にProblem / OSError / BotoCoreError / ClientErrorを捕捉した場合。",
        response="後続の保存が成功すれば再試行APIはHTTP 200、OutboxRow.status=failed、"
        "error_code=context.code。Problemはその業務code、それ以外はexternal_failure。workerはHTTP応答なし。",
        check_procedure="例外型とジョブのerror_codeから実体整合性・外部索引を確認する。",
        remediation_procedure="失敗原因を解消し、同じジョブを再試行する。",
    ),
    MessageId.OCR_FAILED: OperationalMessage(
        level="ERROR",
        summary="OCRエンジンの実行が失敗しました。",
        when="OCR中にOSError / TimeoutExpired / CalledProcessErrorを捕捉した場合。",
        response="後続の保存が成功すればHTTP 201、応答ocr.status=failed、ocr.regions=[]。",
        check_procedure="request_idと例外型からOCRコマンドと日本語辞書の配置を確認する。",
        remediation_procedure="OCR実行環境を復旧して画像を再登録する。",
    ),
    MessageId.EVIDENCE_REJECTED: OperationalMessage(
        level="WARNING",
        summary="整合性を確認できない回答根拠を除外しました。",
        when="根拠の読込み・検証でProblemまたはValueErrorを捕捉した場合。",
        response="HTTPエラーを直ちに返さず根拠を除外して継続。残る有効根拠により回答を返すかstatus=held、履歴はstatus=hidden。",
        check_procedure="request_idと例外型から版・権限・実体の整合性を確認する。",
        remediation_procedure="公開版と索引を照合し、必要なら再索引する。",
    ),
}


class OperationalLogContext(BaseModel):
    """生の例外文・本文・認証情報を受け付けない運用項目。"""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    request_id: UUID | None = Field(description="HTTP要求との相関ID。workerではnull。")
    exception_type: str = Field(
        pattern=r"^[A-Za-z_][A-Za-z0-9_]*$", description="捕捉した例外の型名。"
    )
    status: int | None = Field(
        ge=400, le=599, description="確定したHTTPエラーのstatus。継続処理ではnull。"
    )
    code: str | None = Field(
        description="安全なHTTP応答またはジョブの失敗コード。その他の継続処理ではnull。"
    )
    message: str = Field(description="HTTP応答の安全なメッセージ、またはcatalogの継続結果。")


REQUEST_ID: ContextVar[UUID | None] = ContextVar("request_id", default=None)


class OperationLogger:
    """WARNING/ERRORをcatalogと型付きcontextなしでは出力できない境界。"""

    def __init__(self, name: str) -> None:
        self.logger = logging.getLogger(name)

    def warning(self, message_id: MessageId, *, context_model: OperationalLogContext) -> None:
        self._emit(message_id, context_model, "WARNING")

    def error(self, message_id: MessageId, *, context_model: OperationalLogContext) -> None:
        self._emit(message_id, context_model, "ERROR")

    def _emit(self, message_id: MessageId, context: OperationalLogContext, level: str) -> None:
        if not isinstance(message_id, MessageId) or not isinstance(context, OperationalLogContext):
            raise TypeError("運用ログにはMessageIdとOperationalLogContextが必要です。")
        definition = CATALOG[message_id]
        if definition.level != level:
            raise ValueError("ログレベルがcatalogと一致しません。")
        self.logger.log(
            logging.ERROR if level == "ERROR" else logging.WARNING,
            json.dumps(
                {
                    "message_id": message_id,
                    **definition.model_dump(),
                    "context": context.model_dump(mode="json"),
                },
                ensure_ascii=False,
            ),
        )


ops_logger = OperationLogger("kotorelay.operations")


def continuation_context(message_id: MessageId, error: Exception) -> OperationalLogContext:
    """捕捉して継続する例外の生メッセージを保存せず型と継続結果だけを渡す。"""
    return OperationalLogContext(
        request_id=REQUEST_ID.get(),
        exception_type=type(error).__name__,
        status=None,
        code=(error.code if isinstance(error, Problem) else "external_failure")
        if message_id == MessageId.INDEX_FAILED
        else None,
        message=CATALOG[message_id].response,
    )
