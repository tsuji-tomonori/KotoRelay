"""API GatewayからFastAPIを呼び出す。"""

from mangum import Mangum

from kotorelay.main import app

handler = Mangum(app, lifespan="off")
