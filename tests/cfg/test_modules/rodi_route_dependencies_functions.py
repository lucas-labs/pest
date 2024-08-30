try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated


from typing import Union
from uuid import uuid4

from pest.decorators.controller import controller
from pest.decorators.handler import get
from pest.decorators.module import module
from pest.di import injected


def who_am_i(user: Union[str, None] = None):
    return user if user else str(uuid4())


def yield_me(user: Union[str, None] = None):
    yield user if user else str(uuid4())


@controller('')
class FooController:
    @get('/assigned')
    def assigned(self, me: str = injected(who_am_i)):
        return {'id': me}

    @get('/assigned-with-yield')
    def assign_with_yield(self, me: str = injected(yield_me)):
        return {'id': me}


@controller('')
class FooController39plus:
    @get('/assigned')
    def assigned(self, me: Annotated[str, injected(who_am_i)]):
        return {'id': me}

    @get('/assigned-with-yield')
    def assign_with_yield(self, me: Annotated[str, injected(yield_me)]):
        return {'id': me}


@module(controllers=[FooController])
class FunctionsDependenciesModule:
    pass


@module(controllers=[FooController39plus])
class FunctionsDependenciesModule39plus:
    pass
