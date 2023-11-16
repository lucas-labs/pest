from typing import cast

import pytest
from fastapi.testclient import TestClient

from pest.primitives.application import PestApplication
from pest.primitives.module import Module
from pest.primitives.module import setup_module as _setup_module

from .app.app import bootstrap_app
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
