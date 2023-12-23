try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated


from uuid import uuid4

from pest.decorators.controller import controller
from pest.decorators.handler import get
from pest.decorators.module import module
from pest.di import injected


class Service:
    def __init__(self) -> None:
        self.id = uuid4()

    def who_am_i(self):
        return self.id


@controller('')
class FooController:
    @get('/assigned')
    def assigned(self, svc: Service = injected(Service)):
        assert isinstance(svc, Service)
        return {'id': svc.who_am_i()}

    @get('/assigned-no-token')
    def assigned_no_token(self, svc: Service = injected()):
        assert isinstance(svc, Service)
        return {'id': svc.who_am_i()}

    @get('/noinject')
    def noinject(self):
        # this one is smart enough to know its own id, it doesn't
        # depend on others to tell it who it is :P
        return {'id': uuid4()}


@controller('')
class FooController39plus:
    @get('/annotated')
    def annotated(self, svc: Annotated[Service, injected]):
        assert isinstance(svc, Service)
        return {'id': svc.who_am_i()}


@module(controllers=[FooController], providers=[Service])
class RodiDependenciesModule:
    pass


@module(controllers=[FooController39plus], providers=[Service])
class RodiDependenciesModule39plus:
    pass
