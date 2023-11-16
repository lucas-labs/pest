from pest.decorators.controller import controller
from pest.decorators.module import module


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
    imports=[Mod],
    providers=[ProviderBaz],
    exports=[ProviderBaz],
    controllers=[FooController]
)
class FooModule:
    pass


@module(
    controllers=[FooController],
    providers=[ProviderFoo, ProviderBar, ProviderBaz],
)
class ModuleWithController:
    pass
