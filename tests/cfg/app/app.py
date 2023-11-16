from pest.factory import Pest
from pest.primitives.application import PestApplication

from .app_module import AppModule


def bootstrap_app() -> PestApplication:
    app = Pest.create(root_module=AppModule)

    return app
