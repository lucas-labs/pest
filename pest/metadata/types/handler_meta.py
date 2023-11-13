from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Sequence

from fastapi import Response

from ._meta import Meta, PestType


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
class HandlerMeta(Meta):
    meta_type: PestType = field(default=PestType.HANDLER, init=False)
    methods: list[str]
    path: str
    response_model: Any | None
    response_class: type[Response] | None
    status_code: int | None
    response_model_exclude_none: bool | None
    tags: list[str | Enum] | None
    dependencies: Sequence[Any] | None
    summary: str | None
    description: str | None
    deprecated: bool | None
    name: str | None
    responses: dict[int | str, dict[str, Any]] | None
