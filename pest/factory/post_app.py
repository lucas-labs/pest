from typing import Union

from ..core.application import PestApplication
from ..middleware.types import CorsOptions


def setup(app: PestApplication, cors: Union[CorsOptions, None] = None) -> PestApplication:
    """Initializes stuff that needs the app to already exist to be able to setup"""
    __setup_cors(app, cors)

    return app


def __setup_cors(app: PestApplication, cors: Union[CorsOptions, None]) -> None:
    """Sets up CORS"""
    if cors is None:
        return

    app.enable_cors(**cors)
