from enum import Enum
from typing import Any, Callable, Sequence, TypedDict, TypeVar, Unpack

from pest.decorators._common import meta_decorator

from ..metadata.types import ControllerMeta
from ..primitives.controller import Controller

Class = TypeVar('Class', bound=type)


class ControllerOptions(TypedDict, total=False):
    tags: list[str | Enum] | None
    redirect_slashes: bool | None
    on_startup: Sequence[Callable[[], Any]] | None
    on_shutdown: Sequence[Callable[[], Any]] | None
    deprecated: bool | None
    include_in_schema: bool | None


def controller(
    prefix: str, **options: Unpack[ControllerOptions]
) -> Callable[..., type[Controller]]:
    """🐀 ⇝ decorator that marks a class as a `controller`"""
    return meta_decorator(
        meta_type=ControllerMeta,
        meta={
            'prefix': prefix,
            **options,
        },
        base=Controller,
        singleton=True
    )


def ctrl(prefix: str, **options: Unpack[ControllerOptions]) -> Callable:
    """🐀 ⇝ decorator that marks a class as a `controller`"""
    return controller(prefix, **options)


def router(prefix: str, **options: Unpack[ControllerOptions]) -> Callable:
    """🐀 ⇝ decorator that marks a class as a `router`"""
    return controller(prefix, **options)


def rtr(prefix: str, **options: Unpack[ControllerOptions]) -> Callable:
    """🐀 ⇝ decorator that marks a class as a `router`"""
    return controller(prefix, **options)
