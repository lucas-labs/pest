from abc import ABC
from enum import Enum
from typing import Any, TypeVar

from rodi import ActivationScope, Container, ServiceLifeStyle

import pest.utils.module as module_utils

from ..metadata.types._meta import MetaType
from ..metadata.types.module_meta import (
    ClassProvider,
    ExistingProvider,
    FactoryProvider,
    InjectionToken,
    Provider,
    ValueProvider,
)


class ModuleStatus(str, Enum):
    NOT_INITIALIZED = 'NOT_INITIALIZED'
    INITIALIZING = 'INITIALIZING'
    INITIALIZED = 'INITIALIZED'


def setup_module(module: 'Module') -> None:
    """
    functions that sets up a module. Avoids accessing the
    module's `__setup_module__` method directly
    """
    module.__setup_module__()


T = TypeVar('T')


class Module(ABC):
    __pest_object_type__: MetaType = MetaType.MODULE
    __status__: ModuleStatus
    __imported__providers__: dict[InjectionToken, 'Module']
    imports: list['Module']
    container: Container
    providers: list[Any]
    exports: list[InjectionToken]

    def __init__(self) -> None:
        self.__status__ = ModuleStatus.NOT_INITIALIZED
        self.__imported__providers__ = {}
        self.imports = []
        self.providers = []
        self.exports = []
        self.container = Container()

    def __setup_module__(self) -> None:
        if self.__status__ != ModuleStatus.NOT_INITIALIZED:
            return

        self.__status__ = ModuleStatus.INITIALIZING

        for provider in self.providers:
            self.register(provider)

        for imported_module in self.imports:
            for exported_provider in imported_module.exports:
                self.__imported__providers__[
                    exported_provider
                ] = imported_module

        self.__status__ = ModuleStatus.INITIALIZED

    def register(self, provider: Provider) -> None:
        match provider:
            case ClassProvider(provide, use_class, scope):
                self.container.bind_types(
                    provide,
                    use_class,
                    life_style=scope if scope is not None else ServiceLifeStyle.TRANSIENT
                )
            case FactoryProvider(provide, use_factory, scope):
                self.container.register_factory(
                    factory=use_factory,
                    return_type=provide,
                    life_style=scope if scope is not None else ServiceLifeStyle.TRANSIENT
                )
            case ValueProvider(provide, use_value):
                self.container.add_instance(
                    declared_class=provide,
                    instance=use_value,
                )
            case ExistingProvider(provide, use_existing):
                self.container.add_alias(
                    name=provide,
                    desired_type=use_existing
                )
            case _:
                self.container.add_transient(
                    provider
                )

    def get(self, token: InjectionToken[T], scope: ActivationScope | None = None) -> T:
        if token in self.__imported__providers__:
            return self._get_from_imported(token, scope=scope)

        return self.container.resolve(token, scope=scope)

    def _get_from_imported(
        self,
        token: InjectionToken[T],
        scope: ActivationScope | None = None
    ) -> T:
        return self.__imported__providers__[token].get(token, scope=scope)

    def __str__(self) -> str:
        return module_utils.as_tree(self)
