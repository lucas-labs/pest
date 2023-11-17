from typing import Unpack, cast

from fastapi import APIRouter
from fastapi.routing import APIRoute

from pest.factory.preapp import setup
from pest.logging import LoggingOptions, log

from ..metadata.meta import get_meta_value
from ..primitives.application import PestApplication
from ..primitives.module import setup_module
from ..primitives.types.fastapi_params import FastAPIParams
from ..utils.functions import getset
from . import preapp


class Pest:
    @classmethod
    def create(
        cls,
        root_module: type,
        *,
        prefix: str = '',
        logging: LoggingOptions | None = None,
        **kwargs: Unpack[FastAPIParams]
    ) -> PestApplication:
        """
        🐀 ⇝ creates and initializes a pest application
        #### Params
        - root_module: the root (entry point) module of the application
        - prefix: the prefix for the application's routes
        - logging: logging options (needs `loguru` to be installed)
        """
        preapp.setup(logging)

        name = getset(cast(dict, kwargs), 'title', 'pest 🐀')
        log.info(f'Initializing {name}')

        module_tree = setup_module(root_module)
        routers = module_tree.routers
        app = PestApplication(module=module_tree, **kwargs)

        for router in routers:
            cls.__log_router(router, prefix)
            app.include_router(router, prefix=prefix)

        log.info('Application initialized')

        return app

    @classmethod
    def __log_router(cls, router: APIRouter, prefix: str) -> None:
        log.info(f'Setting up {get_meta_value(router, "name")}')
        for route in cast(list[APIRoute], router.routes):
            for method in route.methods:
                if not route.path.endswith('/'):
                    log.debug(f'{method: <7} {prefix}{route.path}')
