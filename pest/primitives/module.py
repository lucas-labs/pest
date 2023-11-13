from typing import Any, TypeVar

from fastapi import APIRouter
from rodi import ActivationScope, Container, ServiceLifeStyle

import pest.utils.module as module_utils
from pest.metadata.types._meta import PestType

from ..exceptions.base import PestException
from ..metadata.meta import get_meta
from ..metadata.types.module_meta import (
    ClassProvider,
    ExistingProvider,
    FactoryProvider,
    InjectionToken,
    ModuleMeta,
    Provider,
    ValueProvider,
)
from .common import PestPrimitive
from .controller import Controller, setup_controller
from .types.status import Status


def setup_module(
    clazz: type
) -> 'Module':
    """
    functions that sets up a module. Avoids accessing the
    module's `__setup_module__` method directly
    """
    if not issubclass(clazz, Module):
        raise PestException(
            f'{clazz.__name__} is not a module.',
            hint=f'decorate `{clazz.__name__}` with the `@module` decorator (or one of its aliases)'
        )

    module = clazz()
    module.__setup_module__()
    return module


T = TypeVar('T')


class Module(PestPrimitive):
    __imported__providers__: dict[InjectionToken, 'Module']
    imports: list['Module']
    container: Container
    providers: list[Any]
    exports: list[InjectionToken]
    controllers: list[type[Controller]]

    @property
    def routers(self) -> list[APIRouter]:
        return [
            controller.__router__
            for controller in self.controllers
            if controller.__router__ is not None
        ]

    @classmethod
    @property
    def __pest_object_type__(cls) -> PestType:
        return PestType.MODULE

    def __init__(self) -> None:
        self.__class_status__ = Status.NOT_SETUP
        self.__imported__providers__ = {}
        self.imports = []
        self.providers = []
        self.exports = []
        self.container = Container(strict=False)
        self.controllers = []

    def __setup_module__(self) -> None:
        if self.__class_status__ != Status.NOT_SETUP:
            return
        self.__class_status__ = Status.SETTING_UP

        # get module metadata
        meta: ModuleMeta = get_meta(self.__class__, type=ModuleMeta)

        # setup child modules
        for child in meta.imports if meta.imports else []:
            child_instance = setup_module(child)
            self.imports += [child_instance]

        # set internal properties
        self.providers = meta.providers if meta.providers else []
        self.exports = meta.exports if meta.exports else []
        self.controllers = meta.controllers if meta.controllers else []

        # register providers in the di container
        for provider in self.providers:
            self.register(provider)

        # register controllers in the di container
        for controller in self.controllers:
            setup_controller(controller, self)
            self.register(controller)

        # register providers exported by child modules
        for imported_module in self.imports:
            for exported_provider in imported_module.exports:
                self.__imported__providers__[
                    exported_provider
                ] = imported_module

        # we're done
        self.__class_status__ = Status.READY

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

        x = self.container.resolve(token, scope=scope)
        return x

    def _get_from_imported(
        self,
        token: InjectionToken[T],
        scope: ActivationScope | None = None
    ) -> T:
        return self.__imported__providers__[token].get(token, scope=scope)

    def __str__(self) -> str:
        return module_utils.as_tree(self)
