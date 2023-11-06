from typing import Callable, TypedDict, TypeVar, Unpack

from ..decorators._common import meta_decorator
from ..metadata.types import ModuleMeta
from ..metadata.types.module_meta import InjectionToken, Provider
from ..primitives.module import Module

Class = TypeVar('Class', bound=type)


class ModuleOptions(TypedDict, total=False):
    imports: list[type]
    providers: list[Provider]
    exports: list[InjectionToken]


def module(**options: Unpack[ModuleOptions]) -> Callable:
    """🐀 ⇝ decorator that marks a class as a module"""
    return meta_decorator(meta_type=ModuleMeta, meta=options, base=Module, singleton=True)


def mod(**options: Unpack[ModuleOptions]) -> Callable:
    """🐀 ⇝ decorator that marks a class as a module"""
    return module(**options)


def domain(**options: Unpack[ModuleOptions]) -> Callable:
    """🐀 ⇝ decorator that marks a class as a domain module"""
    return module(**options)


def dom(**options: Unpack[ModuleOptions]) -> Callable:
    """🐀 ⇝ decorator that marks a class as a domain module"""
    return module(**options)
