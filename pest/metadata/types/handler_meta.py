from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Sequence, Type, Union

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
    methods: List[str] = field(metadata={'expose': False})
    '''🐀 ⇝ HTTP methods of the handler'''
    path: str = field(metadata={'expose': False})
    '''🐀 ⇝ path of the handler'''
    response_model: Union[Any, None]
    '''🐀 ⇝ response model of the handler'''
    response_class: Union[Type[Response], None]
    '''🐀 ⇝ response class of the handler'''
    status_code: Union[int, None]
    '''🐀 ⇝ status code of the handler'''
    response_model_exclude_none: Union[bool, None]
    '''🐀 ⇝ exclude none values from the response model'''
    tags: Union[List[Union[str, Enum]], None]
    '''🐀 ⇝ tags of the handler'''
    dependencies: Union[Sequence[Any], None]
    '''🐀 ⇝ dependencies of the handler'''
    summary: Union[str, None]
    '''🐀 ⇝ summary of the handler'' '''
    description: Union[str, None]
    '''🐀 ⇝ description of the handler'''
    deprecated: Union[bool, None]
    '''🐀 ⇝ is the handler deprecated?'''
    name: Union[str, None]
    '''🐀 ⇝ name of the handler'''
    responses: Union[Dict[Union[int, str], Dict[str, Any]], None]
    '''🐀 ⇝ responses of the handler'''
