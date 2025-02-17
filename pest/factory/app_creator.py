from contextlib import asynccontextmanager
from typing import AsyncIterator, List, Optional, Union, cast

from fastapi.routing import APIRoute
from starlette.types import Lifespan

from pest.logging import log

from ..core.application import PestApplication
from ..core.module import _on_application_bootstrap, setup_module
from ..core.types.fastapi_params import FastAPIParams
from ..metadata.meta import get_meta_value
from ..middleware.types import CorsOptions, MiddlewareDef
from ..utils.functions import chain_lifespan
from . import openapi


def app_lifespan(
    root_module: type,
    prefix: str,
    cors: Union[CorsOptions, None] = None,
) -> Lifespan['PestApplication']:
    @asynccontextmanager
    async def main_lifespan(app: PestApplication) -> AsyncIterator[None]:
        """main lifespan function

        creates the module tree, appends routes to app and triggers the `on_application_bootstrap`
        lifecycle hooks
        """

        module_tree = await setup_module(root_module)
        app.__pest_module__ = module_tree
        routers = module_tree.routers

        for router in routers:
            # log routes while we add em
            log.info(f'Setting up {get_meta_value(router, "name")}')
            for route in cast(List[APIRoute], router.routes):
                for method in route.methods:
                    full_route = f'{prefix}{route.path}'

                    if full_route == '/' or not full_route.endswith('/'):
                        log.debug(f'{method: <7} {full_route}')

            # add the router
            app.include_router(router, prefix=prefix)

        # recreate the openapi schema to include the new routes and customizations
        openapi.patch(app)

        log.debug(f'{app.title} initialized: \n{app}')

        # trigger the on_application_bootstrap lifecycle hooks on the module tree
        await _on_application_bootstrap(module_tree, app)

        yield

    return main_lifespan


def make_app(
    fastapi_params: FastAPIParams,
    root_module: type,
    lifespan: Optional[Lifespan['PestApplication']] = None,
    middleware: MiddlewareDef = [],
    cors: Union[CorsOptions, None] = None,
    prefix: str = '',
) -> PestApplication:
    """Creates the pest application instance"""
    main_lifespan = app_lifespan(root_module, prefix, cors)
    return PestApplication(
        middleware=middleware,
        lifespan=chain_lifespan(main_lifespan, lifespan) if lifespan else main_lifespan,
        **fastapi_params,
    )
