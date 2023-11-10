

from pest.decorators.controller import controller
from pest.metadata.meta import META_KEY
from pest.metadata.types._meta import MetaType
from pest.primitives.controller import Controller

# aliased porque setup_module es un builtin de pytest


def test_controller_inheritance():
    """🐀 controllers :: @controller :: should make the decorated class inherit from Controller"""
    @controller('/')
    class TestController:
        pass

    assert issubclass(TestController, Controller)
    assert issubclass(TestController, TestController)


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
    class TestController:
        pass

    assert hasattr(TestController, META_KEY)
    meta: dict = getattr(TestController, META_KEY)

    assert meta is not None
    assert isinstance(meta, dict)
    assert meta['meta_type'] == MetaType.CONTROLLER
    assert meta['prefix'] == '/test'
    assert meta['on_startup'] == [cb]
    assert meta['on_shutdown'] == [cb]
    assert meta['deprecated'] is True
    assert meta['redirect_slashes'] is True
