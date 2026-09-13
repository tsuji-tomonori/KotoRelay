"""get_imageの業務結果をHTTP応答用の型へ検証・変換する。"""

from fastapi.responses import Response

from kotorelay.operations.images.get_image.schemas import ResponseData


def build_response(value: ResponseData) -> Response:
    """認可済み画像bytesをPNGの応答として組み立てる。"""
    return Response(value, media_type="image/png")
