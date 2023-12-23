from typing import Callable, TypeVar

try:
    from typing import Unpack
except ImportError:
    from typing_extensions import Unpack

from ..core.module import Module
from ..decorators._common import meta_decorator
from ..metadata.types.module_meta import ModuleMeta
from .dicts.module_dict import ModuleMetaDict

Class = TypeVar('Class', bound=type)


def module(**options: Unpack[ModuleMetaDict]) -> Callable:
    """🐀 ⇝ decorator that marks a class as a module"""
    return meta_decorator(meta=options, base=Module, meta_type=ModuleMeta, singleton=True)


def mod(**options: Unpack[ModuleMetaDict]) -> Callable:
    """🐀 ⇝ decorator that marks a class as a module"""
    return module(**options)


def domain(**options: Unpack[ModuleMetaDict]) -> Callable:
    """🐀 ⇝ decorator that marks a class as a domain module"""
    return module(**options)


def dom(**options: Unpack[ModuleMetaDict]) -> Callable:
    """🐀 ⇝ decorator that marks a class as a domain module"""
    return module(**options)
