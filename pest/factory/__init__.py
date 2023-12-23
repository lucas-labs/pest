try:
    from typing import Unpack, cast
except ImportError:
    from typing_extensions import Unpack, cast

from typing import Union

from ..core.application import PestApplication
from ..core.types.fastapi_params import FastAPIParams
from ..logging import LoggingOptions, log
from ..middleware.types import CorsOptions, MiddlewareDef
from ..utils.functions import getset
from . import post_app, pre_app
from .app_creator import make_app as make_app


class Pest:
    """🐀 ⇝ the main class of the framework, used to create and initialize a pest application"""

    @classmethod
    def create(
        cls,
        root_module: type,
        *,
        logging: Union[LoggingOptions, None] = None,
        middleware: MiddlewareDef = [],
        prefix: str = '',
        cors: Union[CorsOptions, None] = None,
        **fastapi_params: Unpack[FastAPIParams],
    ) -> PestApplication:
        """
        🐀 ⇝ creates and initializes a pest application
        #### Params
        - root_module: the root (entry point) module of the application
        - logging: logging options (needs `loguru` to be installed)
        - middleware: a list of middlewares to be applied to the application
        - prefix: the prefix for the application's routes
        """
        name = getset(cast(dict, fastapi_params), 'title', 'pest 🐀')

        pre_app.setup(logging=logging)
        log.info(f'Initializing {name}')

        app = make_app(fastapi_params, root_module, prefix=prefix, middleware=middleware)
        app = post_app.setup(app, cors=cors)

        log.debug(f'{name} initialized: \n{app}')
        return app
