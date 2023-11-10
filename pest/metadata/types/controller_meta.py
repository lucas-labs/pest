from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Sequence

from starlette.types import Lifespan

from ._meta import Meta, MetaType


@dataclass
class ControllerMeta(Meta):
    meta_type: MetaType = field(default=MetaType.CONTROLLER, init=False)
    prefix: str
    tags: list[str | Enum] | None
    redirect_slashes: bool | None
    on_startup: Sequence[Callable[[], Any]] | None
    on_shutdown: Sequence[Callable[[], Any]] | None
    lifespan: Lifespan[Any] | None
    deprecated: bool | None
    include_in_schema: bool | None
