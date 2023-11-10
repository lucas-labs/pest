from collections.abc import Callable, Sequence
from enum import Enum
from typing import (
    Any,
    TypedDict,
    Unpack,
)

from fastapi.types import DecoratedCallable
from starlette.responses import Response

from pest.decorators._common import meta_decorator

from ..metadata.types.handler_meta import HandlerMeta


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


class HandlerOptions(TypedDict, total=False):
    response_model: Any
    response_class: type[Response]
    status_code: int
    response_model_exclude_none: bool
    tags: list[str | Enum]
    dependencies: Sequence[Any]
    summary: str
    description: str
    deprecated: bool
    name: str
    responses: dict[int | str, dict[str, Any]]


def __make(
    path: str,
    method: HttpMethod,
    **options: Unpack[HandlerOptions]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """utility function to create a handler decorator"""
    return meta_decorator(
        meta_type=HandlerMeta,
        meta={
            'methods': [method],
            'path': path,
            **options,
        }
    )


def get(
    path: str,
    **options: Unpack[HandlerOptions]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """🐀 ⇝ marks a function as a `GET` request handler"""
    return __make(path, HttpMethod.GET, **options)


def post(
    path: str,
    **options: Unpack[HandlerOptions]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """🐀 ⇝ marks a function as a `POST` request handler"""
    return __make(path, HttpMethod.POST, **options)


def put(
    path: str,
    **options: Unpack[HandlerOptions]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """🐀 ⇝ marks a function as a `PUT` request handler"""
    return __make(path, HttpMethod.PUT, **options)


def delete(
    path: str,
    **options: Unpack[HandlerOptions]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """🐀 ⇝ marks a function as a `DELETE` request handler"""
    return __make(path, HttpMethod.DELETE, **options)


def patch(
    path: str,
    **options: Unpack[HandlerOptions]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """🐀 ⇝ marks a function as a `PATCH` request handler"""
    return __make(path, HttpMethod.PATCH, **options)


def options(
    path: str,
    **options: Unpack[HandlerOptions]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """🐀 ⇝ marks a function as a `OPTIONS` request handler"""
    return __make(path, HttpMethod.OPTIONS, **options)


def head(
    path: str,
    **options: Unpack[HandlerOptions]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """🐀 ⇝ marks a function as a `HEAD` request handler"""
    return __make(path, HttpMethod.HEAD, **options)


def trace(
    path: str,
    **options: Unpack[HandlerOptions]
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """🐀 ⇝ marks a function as a `TRACE` request handler"""
    return __make(path, HttpMethod.TRACE, **options)
