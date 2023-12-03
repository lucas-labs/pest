from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Sequence

from starlette.types import Lifespan

from ._meta import Meta, PestType


@dataclass
class ControllerMeta(Meta):
    meta_type: PestType = field(default=PestType.CONTROLLER, init=False, metadata={'expose': False})
    prefix: str = field(metadata={'expose': False})
    tags: list[str | Enum] | None
    '''🐀 ⇝ tags of the controller'''
    redirect_slashes: bool | None
    '''🐀 ⇝ redirect slashes?'''
    on_startup: Sequence[Callable[[], Any]] | None
    '''🐀 ⇝ on startup events'''
    on_shutdown: Sequence[Callable[[], Any]] | None
    '''🐀 ⇝ on shutdown events'''
    lifespan: Lifespan[Any] | None = field(metadata={'expose': False})
    '''🐀 ⇝ lifespan of the controller'''
    deprecated: bool | None
    '''🐀 ⇝ is the controller deprecated?'''
    include_in_schema: bool | None
    '''🐀 ⇝ include in schema?'''
