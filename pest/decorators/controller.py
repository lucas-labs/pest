from typing import Callable, TypeVar, Unpack

from pest.decorators._common import meta_decorator

from ..core.controller import Controller
from ..metadata.types.controller_meta import ControllerMeta
from .dicts.controller_dict import ControllerMetaDict

Class = TypeVar('Class', bound=type)


def controller(
    prefix: str, **options: Unpack[ControllerMetaDict]
) -> Callable[..., type[Controller]]:
    """🐀 ⇝ decorator that marks a class as a `controller`"""
    return meta_decorator(
        meta_type=ControllerMeta,
        meta={
            'prefix': prefix,
            **options,
        },
        base=Controller
    )


def ctrl(prefix: str, **options: Unpack[ControllerMetaDict]) -> Callable:
    """🐀 ⇝ decorator that marks a class as a `controller`"""
    return controller(prefix, **options)


def router(prefix: str, **options: Unpack[ControllerMetaDict]) -> Callable:
    """🐀 ⇝ decorator that marks a class as a `router`"""
    return controller(prefix, **options)


def rtr(prefix: str, **options: Unpack[ControllerMetaDict]) -> Callable:
    """🐀 ⇝ decorator that marks a class as a `router`"""
    return controller(prefix, **options)


def api(prefix: str, **options: Unpack[ControllerMetaDict]) -> Callable:
    """🐀 ⇝ decorator that marks a class as a `router`"""
    return controller(prefix, **options)
