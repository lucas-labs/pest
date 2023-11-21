from pest.core.application import PestApplication
from pest.factory import Pest

from .app_module import AppModule


def bootstrap_app() -> PestApplication:
    app = Pest.create(root_module=AppModule)

    return app
