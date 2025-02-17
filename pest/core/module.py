from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from dij import ActivationScope, Container, ServiceLifeStyle
from fastapi import APIRouter

import pest.utils.module as module_utils
from pest.metadata.types._meta import PestType

from ..exceptions.base.pest import PestException
from ..metadata.meta import get_meta
from ..metadata.types.injectable_meta import (
    ClassProvider,
    ExistingProvider,
    FactoryProvider,
    ValueProvider,
)
from ..metadata.types.module_meta import InjectionToken, ModuleMeta, Provider
from ..utils.functions import classproperty, maybe_coro
from .common import OnApplicationBootstrap, OnModuleInit, PestPrimitive
from .controller import Controller, router_of, setup_controller
from .types.status import Status

if TYPE_CHECKING:
    from .application import PestApplication


def parent_of(module: 'Module') -> Optional['Module']:
    """returns the parent module of a given module"""
    if not isinstance(module, Module):
        raise PestException(
            f'{module.__name__} is not a module.',
            hint=f'decorate `{module.__name__}` with the `@module` decorator '
            '(or one of its aliases)',
        )

    return module.__parent_module__


def contained_in(module: 'Module') -> List[Tuple[InjectionToken, Any]]:
    """returns the providers contained in a given module"""
    if not isinstance(module, Module):
        raise PestException(
            f'{module.__name__} is not a module.',
            hint=f'decorate `{module.__name__}` with the `@module` decorator '
            '(or one of its aliases)',
        )

    return list(module.container)


def assure_module(clazz: type) -> None:
    """assures that a class is a module"""
    if not issubclass(clazz, Module):
        raise PestException(
            f'{clazz.__name__} is not a module.',
            hint=(
                f'decorate `{clazz.__name__}` with the `@module` decorator (or one of its aliases)'
            ),
        )


def assure_module_instance(module: Any) -> None:
    if not isinstance(module, Module):
        raise PestException(
            f'{module.__name__} is not a module.',
            hint=(
                f'decorate `{module.__name__}` with the `@module` decorator (or one of its aliases)'
            ),
        )


async def setup_module(
    clazz: type,
    parent_clazz: Optional['Module'] = None,
) -> 'Module':
    """
    functions that sets up a module. Avoids accessing the
    module's `__setup_module__` method directly
    """
    assure_module(clazz)
    if parent_clazz is not None:
        assure_module_instance(parent_clazz)

    module = clazz()
    await module.__setup_module__(parent_clazz)
    return module


T = TypeVar('T')


async def _on_module_init(module: 'Module') -> None:
    """
    executes the `on_module_init` lifecycle hook for a module, which includes:
    - calling the lifecycle hooks of the module's providers
    - calling the lifecycle hooks of the module's controllers
    - calling the lifecycle hooks of the module itself
    """

    assure_module_instance(module)

    if module.__class_status__ == Status.READY:
        return

    for provider in module.providers:
        # if the provider's scope is singleton/value, we check if the provider has lifecycle
        # hooks and call them if that's the case
        if isinstance(provider, ValueProvider) or (
            hasattr(provider, 'scope') and provider.scope == ServiceLifeStyle.SINGLETON
        ):
            # resolve the provider and try to call the lifecycle hooks
            resolved = module.get(provider.provide)
            if isinstance(resolved, OnModuleInit):
                await maybe_coro(resolved.on_module_init())

    for controller in module.controllers:
        resolved = await maybe_coro(module.aget(cast(Type[Controller], controller)))
        if isinstance(resolved, OnModuleInit):
            await maybe_coro(resolved.on_module_init())

    # and finally, ourselves
    await maybe_coro(module.on_module_init())


async def _on_application_bootstrap(module: 'Module', app: 'PestApplication') -> None:
    """
    executes the `on_application_bootstrap` lifecycle hook for a module, which includes:
    - calling the lifecycle hooks of the module's providers
    - calling the lifecycle hooks of the module's controllers
    - calling the lifecycle hooks of its child modules
    - calling the lifecycle hooks of the module itself
    """

    assure_module_instance(module)

    if module.__class_status__ != Status.READY:
        return

    for child in module.imports:
        await _on_application_bootstrap(child, app)

    for provider in module.providers:
        # if the provider's scope is singleton/value, we check if the provider has lifecycle
        # hooks and call them if that's the case
        if isinstance(provider, ValueProvider) or (
            hasattr(provider, 'scope') and provider.scope == ServiceLifeStyle.SINGLETON
        ):
            # resolve the provider and try to call the lifecycle hooks
            resolved = module.get(provider.provide)
            if isinstance(resolved, OnApplicationBootstrap):
                await maybe_coro(resolved.on_application_bootstrap(app))

    for controller in module.controllers:
        resolved = await maybe_coro(module.aget(cast(Type[Controller], controller)))
        if isinstance(resolved, OnApplicationBootstrap):
            await maybe_coro(resolved.on_application_bootstrap(app))

    # and finally, ourselves
    await maybe_coro(module.on_application_bootstrap(app))


def _create_factory_resolver(provider: InjectionToken, module: 'Module') -> Any:
    async def resolve_from_related() -> Any:
        resolved = await module.aget(cast(InjectionToken, provider))
        return resolved

    return resolve_from_related


class Module(PestPrimitive, OnModuleInit, OnApplicationBootstrap):
    __imported__providers__: Dict[InjectionToken, 'Module']
    __parent_module__: Optional['Module']
    imports: List['Module']
    container: Container
    providers: List[Any]
    exports: List[InjectionToken]
    controllers: List[Type[Controller]]

    @property
    def routers(self) -> List[APIRouter]:
        return self.__get_routers()

    @classproperty
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

    async def __setup_module__(self, parent: Optional['Module']) -> None:
        if self.__class_status__ != Status.NOT_SETUP:
            return
        self.__class_status__ = Status.SETTING_UP

        if parent is not None and isinstance(parent, Module):
            self.__parent_module__ = parent

        # get module metadata
        meta: ModuleMeta = get_meta(self.__class__, ModuleMeta)

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
                self.register(
                    FactoryProvider(
                        provide=provider, use_factory=_create_factory_resolver(provider, parent)
                    )
                )

        # setup child modules
        for child in meta.imports if meta.imports else []:
            child_instance = await setup_module(child, self)
            self.imports += [child_instance]

        # register providers exported by child modules
        for imported_module in self.imports:
            for exported_provider in imported_module.exports:
                self.__imported__providers__[exported_provider] = imported_module

                self.register(
                    FactoryProvider(
                        provide=exported_provider,
                        use_factory=_create_factory_resolver(exported_provider, imported_module),
                    )
                )

        await _on_module_init(self)

        # we're done
        self.__class_status__ = Status.READY

    def register(self, provider: Provider) -> None:
        if isinstance(provider, ClassProvider):
            self.container.bind_types(
                provider.provide,
                provider.use_class,
                life_style=(
                    provider.scope if provider.scope is not None else ServiceLifeStyle.TRANSIENT
                ),
            )
        elif isinstance(provider, FactoryProvider):
            self.container.register_factory(
                factory=provider.use_factory,
                return_type=provider.provide,
                life_style=(
                    provider.scope if provider.scope is not None else ServiceLifeStyle.TRANSIENT
                ),
            )
        elif isinstance(provider, ValueProvider):
            self.container.add_instance(
                declared_class=provider.provide,
                instance=provider.use_value,
            )
        elif isinstance(provider, ExistingProvider):
            self.container.add_alias(name=provider.provide, desired_type=provider.use_existing)
        else:
            self.container.add_transient(provider)

    def can_provide(self, token: InjectionToken) -> bool:
        if token in self.__imported__providers__ or token in self.container:
            return True
        return False

    def __iter__(self) -> Iterator[InjectionToken]:
        for provider, _ in self.container:
            yield provider

    def get(
        self, token: InjectionToken[T], scope: Union[ActivationScope, None] = None, **kwargs: Any
    ) -> T:
        if token in self.__imported__providers__:
            return self.__get_from_imported(token, scope=scope)

        return self.container.resolve(token, scope=scope, **kwargs)

    async def aget(self, token: InjectionToken[T], scope: Union[ActivationScope, None] = None) -> T:
        if token in self.__imported__providers__:
            return await self.__aget_from_imported(token, scope=scope)

        return await self.container.aresolve(token, scope=scope)

    def __get_from_imported(
        self, token: InjectionToken[T], scope: Union[ActivationScope, None] = None
    ) -> T:
        return self.__imported__providers__[token].get(token, scope=scope)

    async def __aget_from_imported(
        self, token: InjectionToken[T], scope: Union[ActivationScope, None] = None
    ) -> T:
        return await self.__imported__providers__[token].aget(token, scope=scope)

    def __get_routers(self) -> List[APIRouter]:
        routers = []
        for controller in self.controllers:
            routers += [router_of(controller)]

        for child in self.imports:
            routers += child.__get_routers()

        return routers

    def __str__(self) -> str:
        return module_utils.as_tree(self)
