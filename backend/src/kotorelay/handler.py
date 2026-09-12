"""API GatewayからFastAPIを呼び出す。"""

from kotorelay.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")
