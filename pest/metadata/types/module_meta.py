from dataclasses import dataclass, field
from typing import Callable, Generic, TypeAlias, TypeVar, Union

from rodi import ServiceLifeStyle

from ...core.controller import Controller
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
    """🐀 ⇝ base class for all providers."""
    provide: InjectionToken
    '''🐀 ⇝ unique injection token'''


@dataclass
class ClassProvider(ProviderBase):
    """🐀 ⇝ defines a `class` type provider"""
    use_class: Class
    '''🐀 ⇝ type (class) of provider (type of the instance to be injected)'''
    scope: Scope | None = None
    '''🐀 ⇝ scope of the provider'''''


@dataclass
class ValueProvider(ProviderBase, Generic[T]):
    """🐀 ⇝ defines a `value` (singleton) type provider"""
    use_value: T
    '''🐀 ⇝ instance to be injected'''


@dataclass
class SingletonProvider(ValueProvider, Generic[T]):
    """🐀 ⇝ defines a `singleton` (value) type provider"""
    pass


@dataclass
class FactoryProvider(ProviderBase, Generic[T]):
    """🐀 ⇝ defines a `factory` type provider"""
    use_factory: Factory[T]
    '''🐀 ⇝ factory function that returns an instance of the provider'''
    scope: Scope | None = None
    '''🐀 ⇝ scope of the provider'''


@dataclass
class ExistingProvider(ProviderBase, Generic[T]):
    """🐀 ⇝ defines an `existing` (aliased) type provider"""
    provide: str
    '''🐀 ⇝ unique injection token of the existing provider'''
    use_existing: InjectionToken
    '''🐀 ⇝ provider to be aliased by the injection token '''


@dataclass
class ModuleMeta(Meta):
    meta_type: PestType = field(default=PestType.MODULE, init=False, metadata={'expose': False})
    imports: list[type] | None
    providers: list[Provider] | None
    exports: list[InjectionToken] | None
    controllers: list[type[Controller]] | None
