from typing import Tuple

import pytest
from fastapi.testclient import TestClient

from pest.core.application import PestApplication
from pest.decorators.controller import controller
from pest.decorators.handler import get
from pest.decorators.module import module
from pest.exceptions.http.http import NotFoundException
from pest.factory import Pest


@controller('/app')
class Ctrl:
    @get('/not-found')
    def fail(self):
        raise NotFoundException()


@module(
    controllers=[Ctrl],
)
class AppModule:
    pass


@pytest.fixture()
def app() -> Tuple[PestApplication, TestClient]:
    app = Pest.create(root_module=AppModule)
    with TestClient(app) as client:
        return app, client


def test_request_scoped_provider(app: Tuple[PestApplication, TestClient]) -> None:
    """🐀 di :: scoped :: should handle PestHttpException"""
    _, client = app

    result = client.get('/app/not-found')
    # expect 404 error code
    assert result.status_code == 404
    assert result.json() == {'code': 404, 'error': 'Not Found', 'message': 'Not Found'}
