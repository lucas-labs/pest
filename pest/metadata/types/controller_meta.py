from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from ._meta import Meta, MetaType


class HttpMethod(str, Enum):
    GET = 'GET'
    HEAD = 'HEAD'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    CONNECT = 'CONNECT'
    OPTIONS = 'OPTIONS'
    TRACE = 'TRACE'
    PATCH = 'PATCH'


@dataclass
class ControllerMeta(Meta):
    meta_type: MetaType = field(default=MetaType.CONTROLLER, init=False)
    path: str
    method: HttpMethod
    handler: Callable[..., Any]
    options: dict[str, Any]
