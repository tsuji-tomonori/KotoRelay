"""get_draftの業務結果をHTTP応答用の型へ検証・変換する。"""

from pydantic import TypeAdapter

from kotorelay.operations.documents.get_draft.schemas import ResponseData


def build_response(value: ResponseData) -> ResponseData:
    """公開する応答型で業務結果を検証し、レスポンスの境界を保証する。"""
    return TypeAdapter(ResponseData).validate_python(value)
