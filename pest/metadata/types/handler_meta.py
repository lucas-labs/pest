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
    meta_type: PestType = field(default=PestType.HANDLER, init=False, metadata={'expose': False})
    methods: list[str] = field(metadata={'expose': False})
    '''🐀 ⇝ HTTP methods of the handler'''
    path: str = field(metadata={'expose': False})
    '''🐀 ⇝ path of the handler'''
    response_model: Any | None
    '''🐀 ⇝ response model of the handler'''
    response_class: type[Response] | None
    '''🐀 ⇝ response class of the handler'''
    status_code: int | None
    '''🐀 ⇝ status code of the handler'''
    response_model_exclude_none: bool | None
    '''🐀 ⇝ exclude none values from the response model'''
    tags: list[str | Enum] | None
    '''🐀 ⇝ tags of the handler'''
    dependencies: Sequence[Any] | None
    '''🐀 ⇝ dependencies of the handler'''
    summary: str | None
    '''🐀 ⇝ summary of the handler'' '''
    description: str | None
    '''🐀 ⇝ description of the handler'''
    deprecated: bool | None
    '''🐀 ⇝ is the handler deprecated?'''
    name: str | None
    '''🐀 ⇝ name of the handler'''
    responses: dict[int | str, dict[str, Any]] | None
    '''🐀 ⇝ responses of the handler'''
