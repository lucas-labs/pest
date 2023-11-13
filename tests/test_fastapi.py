from fastapi.testclient import TestClient

from pest.decorators.controller import controller
from pest.decorators.handler import get
from pest.decorators.module import module
from pest.primitives.application import PestApplication
from pest.primitives.module import setup_module as _setup_module


class FooService:
    def get_bar(self) -> str:
        return 'bar'


@controller('/foo')
class FooController:
    svc: FooService

    @get('/bar')
    def get_a_bar(self):
        return {'msg': self.svc.get_bar()}


@module(
    providers=[FooService],
    controllers=[FooController]
)
class FooModule:
    pass


foo_module = _setup_module(FooModule)
routers = foo_module.routers

app = PestApplication()

for router in routers:
    app.include_router(router)

client = TestClient(app)


def test_read_main():
    """🐀 app :: controller resolution :: should resolve a controller and its dependencies"""
    response = client.get('/foo/bar')
    assert response.status_code == 200
    assert response.json() == {'msg': 'bar'}
