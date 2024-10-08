from typing import cast

from dij import Container
from pytest import raises

from pest.core.common import status
from pest.core.module import Status, parent_of
from pest.core.module import setup_module as _setup_module
from pest.decorators.module import Module, module
from pest.exceptions.base.pest import PestException
from pest.metadata.meta import META_KEY
from pest.metadata.types._meta import PestType

from .cfg.test_modules.pest_primitives import (
    FooController,
    Mod,
    ParentMod,
    ProviderBar,
    ProviderBaz,
    ProviderFoo,
)


def test_module_inheritance():
    """🐀 modules :: @module :: should make the decorated class inherit from Module"""

    @module()
    class TestModule:
        pass

    assert issubclass(TestModule, Module)
    assert issubclass(TestModule, TestModule)


def test_module_meta():
    """🐀 modules :: @module :: should add metadata to the decorated class"""

    class FakeProvider:
        pass

    @module(
        imports=[],
        controllers=[],
        providers=[FakeProvider],
        exports=[FakeProvider],
    )
    class TestModule:
        pass

    assert hasattr(TestModule, META_KEY)
    meta: dict = getattr(TestModule, META_KEY)

    # check it has the right keys
    assert isinstance(meta, dict)
    assert 'meta_type' in meta
    assert meta['meta_type'] == PestType.MODULE

    assert 'imports' in meta
    assert isinstance(meta['imports'], list)
    assert len(meta['imports']) == 0

    assert 'controllers' in meta
    assert isinstance(meta['controllers'], list)
    assert len(meta['controllers']) == 0

    assert 'providers' in meta
    assert isinstance(meta['providers'], list)
    assert len(meta['providers']) == 1
    assert meta['providers'][0] == FakeProvider

    assert 'exports' in meta
    assert isinstance(meta['exports'], list)
    assert len(meta['exports']) == 1
    assert meta['exports'][0] == FakeProvider


def test_module_setup():
    """🐀 modules :: setup_module :: should initialize a module"""
    mod = _setup_module(Mod)

    # check it's an instance of Mod and also of Module
    assert isinstance(mod, Mod)
    assert isinstance(mod, Module)

    # check it's initialized
    assert status(mod) == Status.READY


def test_module_container(mod: Mod):
    """🐀 modules :: module.container :: module should have its own container"""
    container: Container = cast(Container, getattr(mod, 'container', None))
    assert container is not None
    assert isinstance(container, Container)


def test_module_container_has_services(mod: Mod):
    """🐀 modules :: module.container ::
    module container should have the services provided by the module
    """
    container: Container = cast(Container, getattr(mod, 'container', None))

    assert container is not None
    assert isinstance(container, Container)

    assert ProviderBar in container
    assert ProviderFoo in container


def test_module_container_can_resolve_service(mod: Mod):
    """🐀 modules :: module.container ::
    module container should be able to resolve the services provided by the module
    and their dependencies
    """
    container: Container = cast(Container, getattr(mod, 'container', None))

    bar = container.resolve(ProviderBar)
    assert bar is not None
    assert isinstance(bar, ProviderBar)
    assert isinstance(bar.foo, ProviderFoo)
    assert bar.do_the_foo() == 'foo'


def test_di_module_with_controller(module_with_controller: Module):
    """🐀 modules :: module.container ::
    should inject controllers and be able to resolve their dependencies
    """
    assert module_with_controller is not None

    ctrl = module_with_controller.get(FooController)
    assert isinstance(ctrl, FooController)

    baz_svc = getattr(ctrl, 'baz', None)
    bar_svc = getattr(ctrl, 'bar', None)

    assert isinstance(baz_svc, ProviderBaz)
    assert isinstance(bar_svc, ProviderBar)
    assert bar_svc.do_the_foo() == 'foo'
    assert baz_svc.do_the_baz() == 'baz'


def test_module_with_children_setup():
    """🐀 modules :: setup_module (with-children) ::
    should initialize the module and its children
    """
    parent_mod = _setup_module(ParentMod)

    # check it's an instance of ParentMod and also of Module
    assert isinstance(parent_mod, ParentMod)
    assert isinstance(parent_mod, Module)

    # check it's initialized
    assert status(parent_mod) == Status.READY

    # check it has children
    assert len(parent_mod.imports) > 0

    # check all children are initialized
    for child in parent_mod.imports:
        assert status(child) == Status.READY
        assert child.container is not None
        assert isinstance(child.container, Container)


def test_module_di_service_exports(parent_mod: Module):
    """🐀 modules :: module.container (with-children) ::
    module should be able to resolve both its own services and those provided by its children
    """
    child_mod = parent_mod.imports[0]
    parent_container: Container = cast(Container, getattr(parent_mod, 'container', None))
    child_container: Container = cast(Container, getattr(child_mod, 'container', None))

    assert isinstance(parent_container, Container)
    assert isinstance(child_container, Container)

    # check we have our own services
    assert ProviderBaz in parent_container
    baz = parent_container.resolve(ProviderBaz)
    assert baz is not None
    assert isinstance(baz, ProviderBaz)
    assert baz.do_the_baz() == 'baz'

    # check we have the children services in the child container
    assert ProviderBar in child_container
    assert ProviderFoo in child_container

    # check we can resolve the children services from the child module
    bar_from_child = child_mod.get(ProviderBar)
    assert isinstance(bar_from_child, ProviderBar)

    # check we can resolve the children services from the parent module too
    bar_from_parent = parent_mod.get(ProviderBar)
    assert isinstance(bar_from_parent, ProviderBar)


def test_parent_of_fn(parent_mod: Module):
    """🐀 modules :: parent_of :: should return the parent of the module"""

    child = parent_mod.imports[0]
    assert parent_of(child) == parent_mod


def test_parent_of_fn_failing(parent_mod: Module):
    """🐀 modules :: parent_of :: should raise PestException if not a module"""

    class NotAModule:
        pass

    with raises(PestException) as exc_info:
        parent_of(NotAModule)  # type: ignore

    exc = exc_info.value
    assert isinstance(exc, PestException)
    str_ex = str(exc)
    assert 'NotAModule is not a module' in str_ex
    # assert has a hint
    assert '🐀 Hint ⇝' in str_ex
