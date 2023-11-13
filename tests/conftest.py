from typing import cast

import pytest

from pest.decorators.controller import controller
from pest.decorators.module import module
from pest.primitives.module import Module
from pest.primitives.module import setup_module as _setup_module


class ProviderFoo:
    def do_the_foo(self) -> str:
        return 'foo'


class ProviderBar:
    foo: ProviderFoo

    def do_the_foo(self) -> str:
        return self.foo.do_the_foo()


class ProviderBaz:
    def do_the_baz(self) -> str:
        return 'baz'


@module(providers=[ProviderFoo, ProviderBar], exports=[ProviderBar])
class Mod:
    pass


@module(imports=[Mod], providers=[ProviderBaz])
class ParentMod:
    pass


@controller('')
class FooController:
    baz: ProviderBaz
    bar: ProviderBar


@module(
    controllers=[FooController],
    providers=[ProviderFoo, ProviderBar, ProviderBaz],
)
class ModuleWithController:
    pass


@pytest.fixture()
def mod() -> Mod:
    return cast(Mod, _setup_module(Mod))


@pytest.fixture()
def parent_mod() -> Module:
    return _setup_module(ParentMod)


@pytest.fixture()
def module_with_controller() -> Module:
    return _setup_module(ModuleWithController)
