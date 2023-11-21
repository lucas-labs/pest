from typing import Sequence, Unpack, cast

from starlette.middleware import Middleware as StarletteMiddleware

from ..core.application import PestApplication
from ..core.types.fastapi_params import FastAPIParams
from ..logging import LoggingOptions, log
from ..middleware.base import PestMwDispatcher
from ..middleware.types import MiddlewareDef
from ..utils.functions import getset
from . import post_app, pre_app
from .app_creator import make_app as make_app


class Pest:
    @classmethod
    def create(
        cls,
        root_module: type,
        *,
        prefix: str = '',
        middleware: Sequence[StarletteMiddleware | PestMwDispatcher] = [],
        logging: LoggingOptions | None = None,
        **fastapi_params: Unpack[FastAPIParams]
    ) -> PestApplication:
        """
        🐀 ⇝ creates and initializes a pest application
        #### Params
        - root_module: the root (entry point) module of the application
        - prefix: the prefix for the application's routes
        - logging: logging options (needs `loguru` to be installed)
        """
        name = getset(cast(dict, fastapi_params), 'title', 'pest 🐀')
        log.info(f'Initializing {name}')

        pre_app.setup(logging=logging)
        app = make_app(fastapi_params, root_module, prefix=prefix, middleware=middleware)
        app = post_app.setup(app)
        return app
