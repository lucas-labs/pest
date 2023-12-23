from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, List, Sequence, Union

from starlette.types import Lifespan

from ._meta import Meta, PestType


@dataclass
class ControllerMeta(Meta):
    meta_type: PestType = field(default=PestType.CONTROLLER, init=False, metadata={'expose': False})
    prefix: str = field(metadata={'expose': False})
    tags: Union[List[Union[str, Enum]], None]
    '''🐀 ⇝ tags of the controller'''
    redirect_slashes: Union[bool, None]
    '''🐀 ⇝ redirect slashes?'''
    on_startup: Union[Sequence[Callable[[], Any]], None]
    '''🐀 ⇝ on startup events'''
    on_shutdown: Union[Sequence[Callable[[], Any]], None]
    '''🐀 ⇝ on shutdown events'''
    lifespan: Union[Lifespan[Any], None] = field(metadata={'expose': False})
    '''🐀 ⇝ lifespan of the controller'''
    deprecated: Union[bool, None]
    '''🐀 ⇝ is the controller deprecated?'''
    include_in_schema: Union[bool, None]
    '''🐀 ⇝ include in schema?'''
