from typing import cast

from fastapi.routing import APIRoute

from pest.logging import log

from ..core.application import PestApplication
from ..core.module import setup_module
from ..core.types.fastapi_params import FastAPIParams
from ..metadata.meta import get_meta_value
from ..middleware.types import MiddlewareDef


def make_app(
    fastapi_params: FastAPIParams,
    root_module: type,
    middleware: MiddlewareDef = [],
    prefix: str = '',
) -> PestApplication:
    """Creates the pest application instance"""
    module_tree = setup_module(root_module)
    routers = module_tree.routers
    app = PestApplication(module=module_tree, middleware=middleware, **fastapi_params)

    for router in routers:
        # log routes while we add em
        log.info(f'Setting up {get_meta_value(router, "name")}')
        for route in cast(list[APIRoute], router.routes):
            for method in route.methods:
                if not route.path.endswith('/'):
                    log.debug(f'{method: <7} {prefix}{route.path}')

        # add the router
        app.include_router(router, prefix=prefix)

    return app
