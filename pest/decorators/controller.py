from typing import Callable, Type, TypeVar

try:
    from typing import Unpack
except ImportError:
    from typing_extensions import Unpack


from pest.decorators._common import meta_decorator

from ..core.controller import Controller
from ..metadata.types.controller_meta import ControllerMeta
from .dicts.controller_dict import ControllerMetaDict

Class = TypeVar('Class', bound=type)


def controller(
    prefix: str, **options: Unpack[ControllerMetaDict]
) -> Callable[..., Type[Controller]]:
    """🐀 ⇝ decorator that marks a class as a `controller`"""
    controller_prefix: str | None = prefix

    if prefix == '/':
        controller_prefix = None

    return meta_decorator(
        meta_type=ControllerMeta,
        meta={
            'prefix': controller_prefix,
            **options,
        },
        base=Controller,
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
