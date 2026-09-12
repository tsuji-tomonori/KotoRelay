"""実行環境と処理上限を環境変数で設定する。"""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KOTORELAY_")
    mode: Literal["local", "aws"] = "local"
    database_url: str = "postgresql://kotorelay:kotorelay-local@localhost:5432/kotorelay"
    organization_id: str = "00000000-0000-0000-0000-000000000001"
    object_root: str = ".workspace/objects"
    bucket: str = ""
    dsql_host: str = ""
    dsql_user: str = "kotorelay_app"
    region: str = "ap-northeast-1"
    issuer: str = ""
    client_id: str = ""
    model_id: str = "amazon.nova-lite-v1:0"
    vector_bucket: str = ""
    vector_index: str = "knowledge"
    embedding_model: str = "amazon.titan-embed-text-v2:0"
    max_questions_per_day: int = 100
    max_model_images: int = 5
    max_image_bytes: int = 5 * 1024 * 1024
    max_image_pixels: int = 20_000_000
    max_document_images: int = 10
    ocr_command: str = "tesseract"
    frontend_origin: str = "http://localhost:4321"
