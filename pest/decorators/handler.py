from enum import Enum
from typing import Callable

try:
    from typing import Unpack
except ImportError:
    from typing_extensions import Unpack

from fastapi.types import DecoratedCallable

from pest.decorators._common import meta_decorator

from ..metadata.types.handler_meta import HandlerMeta
from .dicts.handler_dict import HandlerMetaDict


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


def __make(
    path: str, method: HttpMethod, **options: Unpack[HandlerMetaDict]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """utility function to create a handler decorator"""
    return meta_decorator(
        meta_type=HandlerMeta,
        meta={
            'methods': [method],
            'path': path,
            **options,
        },
    )


def get(
    path: str, **options: Unpack[HandlerMetaDict]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """🐀 ⇝ marks a function as a `GET` request handler"""
    return __make(path, HttpMethod.GET, **options)


def post(
    path: str, **options: Unpack[HandlerMetaDict]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """🐀 ⇝ marks a function as a `POST` request handler"""
    return __make(path, HttpMethod.POST, **options)


def put(
    path: str, **options: Unpack[HandlerMetaDict]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """🐀 ⇝ marks a function as a `PUT` request handler"""
    return __make(path, HttpMethod.PUT, **options)


def delete(
    path: str, **options: Unpack[HandlerMetaDict]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """🐀 ⇝ marks a function as a `DELETE` request handler"""
    return __make(path, HttpMethod.DELETE, **options)


def patch(
    path: str, **options: Unpack[HandlerMetaDict]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """🐀 ⇝ marks a function as a `PATCH` request handler"""
    return __make(path, HttpMethod.PATCH, **options)


def options(
    path: str, **options: Unpack[HandlerMetaDict]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """🐀 ⇝ marks a function as a `OPTIONS` request handler"""
    return __make(path, HttpMethod.OPTIONS, **options)


def head(
    path: str, **options: Unpack[HandlerMetaDict]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """🐀 ⇝ marks a function as a `HEAD` request handler"""
    return __make(path, HttpMethod.HEAD, **options)


def trace(
    path: str, **options: Unpack[HandlerMetaDict]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """🐀 ⇝ marks a function as a `TRACE` request handler"""
    return __make(path, HttpMethod.TRACE, **options)
