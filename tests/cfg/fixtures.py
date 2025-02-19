try:
    from typing import TypeAlias, cast
except ImportError:
    from typing_extensions import TypeAlias, cast

from typing import Tuple

import pytest
from fastapi import Request, Response
from fastapi.testclient import TestClient
from starlette.middleware.base import RequestResponseEndpoint

from pest.core.application import PestApplication
from pest.core.module import Module
from pest.core.module import setup_module as _setup_module
from pest.factory import Pest
from tests.cfg.test_modules.di_scopes_primitives import Scoped, Transient

from .test_apps.guards_app import app as guards_app
from .test_apps.multi_singleton_app import app as multi_singleton_app
from .test_apps.todo_app import app as todo_app
from .test_modules.di_scopes_primitives import DIScopesModule, Singleton
from .test_modules.fastapi_dependencies import FastApiDependenciesModule
from .test_modules.fastapi_params import FastApiParamsModule
from .test_modules.pest_primitives import (
    Mod,
    ModuleWithController,
    ParentMod,
)

TestApp: TypeAlias = Tuple[PestApplication, TestClient]


@pytest.fixture()
async def mod() -> Mod:
    return cast(Mod, await _setup_module(Mod))


@pytest.fixture()
async def parent_mod() -> Module:
    return await _setup_module(ParentMod)


@pytest.fixture()
async def module_with_controller() -> Module:
    return await _setup_module(ModuleWithController)


@pytest.fixture()
def app_n_client() -> TestApp:
    app = todo_app.bootstrap_app()
    with TestClient(app) as client:
        return app, client


@pytest.fixture()
def multiple_singletons_app() -> TestApp:
    app = multi_singleton_app.bootstrap_app()
    with TestClient(app) as client:
        return app, client


@pytest.fixture()
def guards_annotated_app() -> TestApp:
    app = guards_app.bootstrap_app()
    with TestClient(app) as client:
        return app, client


@pytest.fixture()
def di_app_n_client() -> TestApp:
    app = Pest.create(root_module=DIScopesModule)

    @app.middleware('http')
    async def middleware(
        request: Request,
        call_next: RequestResponseEndpoint,
        scoped: Scoped,
        singleton: Singleton,
        transient: Transient,
    ) -> Response:
        response = await call_next(request)
        response.headers['Scoped-Id'] = str(scoped.get_id())
        response.headers['Singleton-Id'] = str(singleton.get_id())
        response.headers['Transient-Id'] = str(transient.get_id())
        return response

    with TestClient(app) as client:
        return app, client


@pytest.fixture()
def fastapi_params_app() -> TestApp:
    app = Pest.create(root_module=FastApiParamsModule)
    with TestClient(app) as client:
        return app, client


@pytest.fixture()
def fastapi_dependencies_app() -> TestApp:
    app = Pest.create(root_module=FastApiDependenciesModule)

    with TestClient(app) as client:
        return app, client
