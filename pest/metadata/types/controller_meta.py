from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Sequence

from starlette.types import Lifespan

from ._meta import Meta, PestType


@dataclass
class ControllerMeta(Meta):
    meta_type: PestType = field(
        default=PestType.CONTROLLER,
        init=False,
        metadata={'expose': False}
    )
    prefix: str = field(metadata={'expose': False})
    tags: list[str | Enum] | None
    redirect_slashes: bool | None
    on_startup: Sequence[Callable[[], Any]] | None
    on_shutdown: Sequence[Callable[[], Any]] | None
    lifespan: Lifespan[Any] | None = field(metadata={'expose': False})
    deprecated: bool | None
    include_in_schema: bool | None
