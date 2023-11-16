from dataclasses import dataclass, field
from typing import Callable, Generic, TypeAlias, TypeVar, Union

from rodi import ServiceLifeStyle

from ...primitives.controller import Controller
from ._meta import Meta, PestType

T = TypeVar('T')

InjectionToken: TypeAlias = str | type | type[T]
Class: TypeAlias = type
Factory: TypeAlias = Callable[..., T]
Scope: TypeAlias = ServiceLifeStyle
Provider: TypeAlias = Union[
    Class,
    'ValueProvider',
    'FactoryProvider',
    'ExistingProvider',
    'ClassProvider'
]


@dataclass
class ProviderBase():
    provide: InjectionToken


@dataclass
class ClassProvider(ProviderBase):
    use_class: Class
    scope: Scope | None = None


@dataclass
class ValueProvider(ProviderBase, Generic[T]):
    use_value: T


@dataclass
class FactoryProvider(ProviderBase, Generic[T]):
    use_factory: Factory[T]
    scope: Scope | None = None


@dataclass
class ExistingProvider(ProviderBase, Generic[T]):
    provide: str
    use_existing: InjectionToken


@dataclass
class ModuleMeta(Meta):
    meta_type: PestType = field(default=PestType.MODULE, init=False, metadata={'expose': False})
    imports: list[type] | None
    providers: list[Provider] | None
    exports: list[InjectionToken] | None
    controllers: list[type[Controller]] | None
