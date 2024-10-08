from dataclasses import dataclass, field
from typing import Callable, Generic, Type, TypeVar, Union

from dij import ServiceLifeStyle

from ._meta import Meta, PestType

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

T = TypeVar('T')


Factory: TypeAlias = Callable[..., T]
Scope: TypeAlias = ServiceLifeStyle
InjectionToken: TypeAlias = Union[type, Type[T]]
Class: TypeAlias = type


@dataclass
class InjectableMeta(Meta):
    meta_type: PestType = field(default=PestType.INJECTABLE, init=False)


@dataclass
class ProviderBase:
    """🐀 ⇝ base class for all providers."""

    provide: InjectionToken
    '''🐀 ⇝ unique injection token'''


@dataclass
class ClassProvider(ProviderBase):
    """🐀 ⇝ defines a `class` type provider"""

    use_class: Class
    '''🐀 ⇝ type (class) of provider (type of the instance to be injected 💉)'''
    scope: Union[Scope, None] = None
    '''🐀 ⇝ scope of the provider''' ''


@dataclass
class ValueProvider(ProviderBase, Generic[T]):
    """🐀 ⇝ defines a `value` (singleton) type provider"""

    use_value: T
    '''🐀 ⇝ instance to be injected 💉'''


@dataclass
class SingletonProvider(ValueProvider, Generic[T]):
    """🐀 ⇝ defines a `singleton` (value) type provider"""

    pass


@dataclass
class FactoryProvider(ProviderBase, Generic[T]):
    """🐀 ⇝ defines a `factory` type provider"""

    use_factory: Factory[T]
    '''🐀 ⇝ factory function that returns an instance of the provider'''
    scope: Union[Scope, None] = None
    '''🐀 ⇝ scope of the provider'''


@dataclass
class ExistingProvider(ProviderBase, Generic[T]):
    """🐀 ⇝ defines an `existing` (aliased) type provider"""

    provide: str
    '''🐀 ⇝ unique injection token of the existing provider'''
    use_existing: InjectionToken
    '''🐀 ⇝ provider to be aliased by the injection token '''
