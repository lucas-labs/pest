from dataclasses import dataclass, field
from typing import List, Type, Union

from ...core.controller import Controller
from ._meta import Meta, PestType
from .injectable_meta import (
    ClassProvider,
    ExistingProvider,
    FactoryProvider,
    InjectionToken,
    ValueProvider,
)

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias


Class: TypeAlias = type
Provider: TypeAlias = Union[
    Class, 'ValueProvider', 'FactoryProvider', 'ExistingProvider', 'ClassProvider'
]


@dataclass
class ModuleMeta(Meta):
    meta_type: PestType = field(default=PestType.MODULE, init=False, metadata={'expose': False})

    imports: Union[List[type], None]
    '''🐀 ⇝ list of modules to be imported'''

    providers: Union[List[Provider], None]
    '''🐀 ⇝ list of providers to be registered'''

    exports: Union[List[InjectionToken], None]
    '''🐀 ⇝ list of providers to be exported'''

    controllers: Union[List[Type[Controller]], None]
    '''🐀 ⇝ list of controllers to be registered'''
