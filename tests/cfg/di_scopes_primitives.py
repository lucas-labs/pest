from pest.decorators.controller import controller
from pest.decorators.handler import get
from pest.decorators.module import module
from pest.metadata.types.module_meta import ClassProvider, Scope


class Scoped:
    def get_id(self) -> int:
        return id(self)


class Singleton:
    def get_id(self) -> int:
        return id(self)


class Transient:
    def get_id(self) -> int:
        return id(self)


class Dependent:
    scoped_svc: Scoped
    singleton_svc: Singleton
    transient_svc: Transient

    def get_scoped_id(self) -> int:
        return self.scoped_svc.get_id()

    def get_singleton_id(self) -> int:
        return self.singleton_svc.get_id()

    def get_transient_id(self) -> int:
        return self.transient_svc.get_id()


@controller('/scopes')
class Controller:
    # controller to test request-scoped services
    dependent: Dependent
    scoped: Scoped
    singleton: Singleton
    transient: Transient

    @get('/scoped')
    def get_id(self) -> list[int]:
        # they all should have the same id for the same request
        # but different ids for different requests
        return [
            self.dependent.get_scoped_id(),
            self.scoped.get_id(),
            id(self.scoped)
        ]

    @get('/singleton')
    def get_singleton_id(self) -> list[int]:
        # they all should have the same id across requests
        return [
            self.dependent.get_singleton_id(),
            self.singleton.get_id(),
            id(self.singleton)
        ]

    @get('/transient')
    def get_transient_id(self) -> list[int]:
        # they all should have different ids across requests
        return [
            self.dependent.get_transient_id(),
            self.transient.get_id(),
        ]


@module(
    providers=[
        ClassProvider(
            provide=Scoped,
            use_class=Scoped,
            scope=Scope.SCOPED
        ),
        ClassProvider(
            provide=Singleton,
            use_class=Singleton,
            scope=Scope.SINGLETON
        ),
        ClassProvider(
            provide=Transient,
            use_class=Transient,
            scope=Scope.TRANSIENT
        ),
        Dependent
    ],
    controllers=[Controller]
)
class DIScopesModule():
    pass
