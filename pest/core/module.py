from typing import Any, Optional, TypeVar, cast

from fastapi import APIRouter
from rodi import ActivationScope, Container, ServiceLifeStyle

import pest.utils.module as module_utils
from pest.metadata.types._meta import PestType

from ..exceptions.base.pest import PestException
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
from .controller import Controller, router_of, setup_controller
from .types.status import Status


def parent_of(module: 'Module') -> Optional['Module']:
    """returns the parent module of a given module"""
    if not isinstance(module, Module):
        raise PestException(
            f'{module.__name__} is not a module.',
            hint=f'decorate `{module.__name__}` with the `@module` decorator '
            '(or one of its aliases)',
        )

    return module.__parent_module__


def contained_in(module: 'Module') -> list[tuple[InjectionToken, Any]]:
    """returns the providers contained in a given module"""
    if not isinstance(module, Module):
        raise PestException(
            f'{module.__name__} is not a module.',
            hint=f'decorate `{module.__name__}` with the `@module` decorator '
            '(or one of its aliases)',
        )

    return list(module.container)


def setup_module(
    clazz: type,
    parent_clazz: Optional['Module'] = None,
) -> 'Module':
    """
    functions that sets up a module. Avoids accessing the
    module's `__setup_module__` method directly
    """
    if not issubclass(clazz, Module):
        raise PestException(
            f'{clazz.__name__} is not a module.',
            hint=(
                f'decorate `{clazz.__name__}` with the `@module` decorator (or one of its aliases)'
            ),
        )

    if parent_clazz is not None and not isinstance(parent_clazz, Module):
        raise PestException(
            f'{parent_clazz.__name__} is not a module.',
            hint=(
                f'decorate `{parent_clazz.__name__}` with the `@module` '
                'decorator (or one of its aliases)'
            ),
        )

    module = clazz()
    module.__setup_module__(parent_clazz)
    return module


T = TypeVar('T')


class Module(PestPrimitive):
    __imported__providers__: dict[InjectionToken, 'Module']
    __parent_module__: Optional['Module']
    imports: list['Module']
    container: Container
    providers: list[Any]
    exports: list[InjectionToken]
    controllers: list[type[Controller]]

    @property
    def routers(self) -> list[APIRouter]:
        return self.__get_routers()

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

    def __setup_module__(self, parent: Optional['Module']) -> None:
        if self.__class_status__ != Status.NOT_SETUP:
            return
        self.__class_status__ = Status.SETTING_UP

        if parent is not None and isinstance(parent, Module):
            self.__parent_module__ = parent

        # get module metadata
        meta: ModuleMeta = get_meta(self.__class__, type=ModuleMeta)

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

        # register parent providers as factory providers here, so that we
        # can have access to services provided by the parent module
        # or globally (in the root module)
        if parent is not None:
            for provider, _ in contained_in(parent):

                def resolve_from_parent() -> Any:
                    return parent.get(cast(InjectionToken, provider))

                self.register(FactoryProvider(provide=provider, use_factory=resolve_from_parent))

        # setup child modules
        for child in meta.imports if meta.imports else []:
            child_instance = setup_module(child, self)
            self.imports += [child_instance]

        # register providers exported by child modules
        for imported_module in self.imports:
            for exported_provider in imported_module.exports:
                self.__imported__providers__[exported_provider] = imported_module

        # we're done
        self.__class_status__ = Status.READY

    def register(self, provider: Provider) -> None:
        match provider:
            case ClassProvider(provide, use_class, scope):
                self.container.bind_types(
                    provide,
                    use_class,
                    life_style=scope if scope is not None else ServiceLifeStyle.TRANSIENT,
                )
            case FactoryProvider(provide, use_factory, scope):
                self.container.register_factory(
                    factory=use_factory,
                    return_type=provide,
                    life_style=scope if scope is not None else ServiceLifeStyle.TRANSIENT,
                )
            case ValueProvider(provide, use_value):
                self.container.add_instance(
                    declared_class=provide,
                    instance=use_value,
                )
            case ExistingProvider(provide, use_existing):
                self.container.add_alias(name=provide, desired_type=use_existing)
            case _:
                self.container.add_transient(provider)

    def can_provide(self, token: InjectionToken) -> bool:
        if token in self.__imported__providers__ or token in self.container:
            return True
        return False

    def get(self, token: InjectionToken[T], scope: ActivationScope | None = None) -> T:
        if token in self.__imported__providers__:
            return self.__get_from_imported(token, scope=scope)

        return self.container.resolve(token, scope=scope)

    def __get_from_imported(
        self, token: InjectionToken[T], scope: ActivationScope | None = None
    ) -> T:
        return self.__imported__providers__[token].get(token, scope=scope)

    def __get_routers(self) -> list[APIRouter]:
        routers = []
        for controller in self.controllers:
            routers += [router_of(controller)]

        for child in self.imports:
            routers += child.__get_routers()

        return routers

    def __str__(self) -> str:
        return module_utils.as_tree(self)
