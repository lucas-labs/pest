from fastapi.routing import APIRoute

from pest.core.common import primitive_type, status
from pest.core.controller import Controller, router_of, setup_controller
from pest.core.types.status import Status
from pest.decorators.controller import controller
from pest.decorators.handler import get
from pest.metadata.meta import META_KEY
from pest.metadata.types._meta import PestType
from pest.utils.fastapi.router import PestRouter

# aliased porque setup_module es un builtin de pytest


def test_controller_inheritance():
    """🐀 controllers :: @controller :: should make the decorated class inherit from Controller"""

    @controller('/')
    class FooController:
        pass

    assert issubclass(FooController, Controller)
    assert issubclass(FooController, FooController)


def test_controller_meta():
    """🐀 controllers :: @controller :: should add metadata to the decorated class"""

    def cb() -> None:
        pass

    @controller(
        '/test',
        on_startup=[cb],
        on_shutdown=[cb],
        deprecated=True,
        redirect_slashes=True,
        include_in_schema=True,
    )
    class FooController:
        pass

    assert primitive_type(FooController) == PestType.CONTROLLER
    assert hasattr(FooController, META_KEY)
    meta: dict = getattr(FooController, META_KEY)

    assert meta is not None
    assert isinstance(meta, dict)
    assert meta['meta_type'] == PestType.CONTROLLER
    assert meta['prefix'] == '/test'
    assert meta['on_startup'] == [cb]
    assert meta['on_shutdown'] == [cb]
    assert meta['deprecated'] is True
    assert meta['redirect_slashes'] is True


def test_controller_setup():
    """🐀 controllers :: __setup_controller_class__ :: should setup the controller's router""" ''

    @controller('/foo')
    class FooController:
        pass

    setup_controller(FooController)

    assert status(FooController) == Status.READY
    router = router_of(FooController)

    assert isinstance(router, PestRouter)
    assert router.prefix == '/foo'


def test_controller_handlers_setup():
    """🐀 controllers :: __setup_controller_class__ :: should setup the controller's handlers"""

    @controller('/foo')
    class FooController:
        @get('/bar')
        def bar_handler(self) -> str:
            return 'bar'

        def no_handler(self) -> str:
            return 'no'

    setup_controller(FooController)
    assert status(FooController) == Status.READY

    router = router_of(FooController)
    assert len(router.routes) == 2

    route = router.routes[0]
    route_slash = router.routes[1]

    assert isinstance(route, APIRoute)
    assert isinstance(route_slash, APIRoute)
    assert route.path == '/foo/bar'
    assert route_slash.path == '/foo/bar/'
