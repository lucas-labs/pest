from typing import cast

import pytest
from fastapi import Request, Response
from fastapi.testclient import TestClient
from starlette.middleware.base import RequestResponseEndpoint

from pest.core.application import PestApplication
from pest.core.module import Module
from pest.core.module import setup_module as _setup_module
from pest.factory import Pest
from tests.cfg.di_scopes_primitives import Scoped, Transient

from .app.app import bootstrap_app
from .di_scopes_primitives import DIScopesModule, Singleton
from .pest_primitives import (
    Mod,
    ModuleWithController,
    ParentMod,
)


@pytest.fixture()
def mod() -> Mod:
    return cast(Mod, _setup_module(Mod))


@pytest.fixture()
def parent_mod() -> Module:
    return _setup_module(ParentMod)


@pytest.fixture()
def module_with_controller() -> Module:
    return _setup_module(ModuleWithController)


@pytest.fixture()
def app_n_client() -> tuple[PestApplication, TestClient]:
    app = bootstrap_app()
    client = TestClient(app)
    return app, client


@pytest.fixture()
def di_app_n_client() -> tuple[PestApplication, TestClient]:
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

    client = TestClient(app)
    return app, client
