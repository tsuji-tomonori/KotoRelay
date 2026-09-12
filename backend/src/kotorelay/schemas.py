"""API入出力と不変manifestを検証する。"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Id = Annotated[
    str, Field(pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Placement(Input):
    id: Id
    asset_id: Id
    ocr_run_id: Id
    offset: int = Field(ge=0, le=100_000)
    heading: str = Field(default="", max_length=200)


class Region(Input):
    text: str = Field(max_length=5000)
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(ge=0, le=1)
    height: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    order: int = Field(ge=0)


class OcrResult(Input):
    regions: list[Region] = Field(max_length=1000)
    engine: str = Field(max_length=100)
    status: Literal["ready", "failed"]


class CreateDocument(Input):
    title: str = Field(min_length=1, max_length=200)
    department_id: Id


class SaveDraft(Input):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(max_length=100_000)
    revision: int = Field(ge=1)
    placements: list[Placement] = Field(default_factory=list, max_length=10)


class Submit(Input):
    revision: int = Field(ge=1)


class Decide(Input):
    manifest_hash: str = Field(pattern="^[0-9a-f]{64}$")
    decision: Literal["approved", "rejected"]
    reason: str = Field(default="", max_length=2000)


class ChangePolicy(Input):
    revision: int = Field(ge=1)
    visibility: Literal["department", "selected", "organization"]
    shared_departments: list[Id] = Field(default_factory=list, max_length=30)
    status: Literal["active", "withdrawn", "deleted"]


class ChangeMembership(Input):
    user_id: Id
    department_id: Id
    leader: bool = False
    can_author: bool = False
    can_review: bool = False
    active: bool = True


class Ask(Input):
    question: str = Field(min_length=1, max_length=2000)
    department_id: Id
    conversation_id: Id | None = None


class ViewEvent(Input):
    id: Id
    department_id: Id


class OcrCorrection(Input):
    regions: list[Region] = Field(max_length=1000)
    confirmed: bool


class ManifestImage(BaseModel):
    placement: Placement
    image_hash: str
    ocr_hash: str


class Manifest(BaseModel):
    body_hash: str
    images: list[ManifestImage]
    format_version: str = "kotorelay-manifest-v1"


class Citation(BaseModel):
    document_id: str
    version_id: str
    chunk_id: str
    title: str
    heading: str
    manifest_hash: str
    chunk_hash: str
    document_revision: int


class Evidence(BaseModel):
    citations: list[Citation]


class AnswerView(BaseModel):
    id: str
    conversation_id: str
    question: str
    answer: str
    status: str
    citations: list[Citation]
    model: str
    created_at: datetime


class ErrorResponse(BaseModel):
    code: str
    message: str
    request_id: str
