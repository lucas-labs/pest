from uuid import uuid4

from pest.decorators.controller import controller
from pest.decorators.handler import get
from pest.decorators.module import module
from pest.metadata.types.injectable_meta import ClassProvider, Scope


class Scoped:
    def __init__(self) -> None:
        self.id = uuid4()

    def get_id(self):
        # return id(self)
        return self.id


class Singleton:
    def __init__(self) -> None:
        self.id = uuid4()

    def get_id(self):
        return self.id


class Transient:
    def __init__(self) -> None:
        self.id = uuid4()

    def get_id(self):
        return self.id


class Dependent:
    scoped_svc: Scoped
    singleton_svc: Singleton
    transient_svc: Transient

    def get_scoped_id(self):
        return self.scoped_svc.get_id()

    def get_singleton_id(self):
        return self.singleton_svc.get_id()

    def get_transient_id(self):
        return self.transient_svc.get_id()


@controller('/scopes')
class Controller:
    # controller to test request-scoped services
    dependent: Dependent
    scoped: Scoped
    singleton: Singleton
    transient: Transient

    @get('/scoped')
    def get_id(self):
        # they all should have the same id for the same request
        # but different ids for different requests
        return [self.dependent.get_scoped_id(), self.scoped.get_id()]

    @get('/singleton')
    def get_singleton_id(self):
        # they all should have the same id across requests
        return [self.dependent.get_singleton_id(), self.singleton.get_id()]

    @get('/transient')
    def get_transient_id(self):
        # they all should have different ids across requests
        return [
            self.dependent.get_transient_id(),
            self.transient.get_id(),
        ]


@module(
    providers=[
        ClassProvider(provide=Scoped, use_class=Scoped, scope=Scope.SCOPED),
        ClassProvider(provide=Singleton, use_class=Singleton, scope=Scope.SINGLETON),
        ClassProvider(provide=Transient, use_class=Transient, scope=Scope.TRANSIENT),
        Dependent,
    ],
    controllers=[Controller],
)
class DIScopesModule:
    pass
