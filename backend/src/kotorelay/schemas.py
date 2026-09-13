"""API間で共有する値型、manifest、エラー型を定義する。"""

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
    alt_text: str = Field(default="", max_length=1000)
    caption: str = Field(default="", max_length=2000)


class Region(Input):
    region_id: Id | None = None
    source: Literal["detected", "human"] = "detected"
    text: str = Field(max_length=5000)
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(ge=0, le=1)
    height: float = Field(ge=0, le=1)
    confidence: float | None = Field(default=None, ge=0, le=1)
    order: int = Field(ge=0)


class OcrResult(Input):
    confirmed: bool = False
    regions: list[Region] = Field(max_length=1000)
    engine: str = Field(max_length=100)
    status: Literal["ready", "failed"]


class ManifestImage(BaseModel):
    placement: Placement
    image_hash: str
    ocr_hash: str


class Manifest(BaseModel):
    body_hash: str
    images: list[ManifestImage]
    format_version: str = "kotorelay-manifest-v1"


class Citation(BaseModel):
    version_number: int | None = None
    has_images: bool = False
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
