from abc import ABC
from typing import Callable, TypedDict, TypeVar, Unpack

from ..metadata.types import InjectableMeta, MetaType
from ._common import meta_decorator

Cls = TypeVar('Cls', bound=type)


class Injectable(ABC):
    __pest_object_type__: MetaType = MetaType.INJECTABLE


class InjectableOptions(TypedDict, total=False):
    pass


def injectable(**options: Unpack[InjectableOptions]) -> Callable:
    """🐀 ⇝ decorator that marks a class as an injectable service"""
    return meta_decorator(meta_type=InjectableMeta, meta=options, base=Injectable)


def service(**options: Unpack[InjectableOptions]) -> Callable:
    """🐀 ⇝ decorator that marks a class as an injectable service"""
    return injectable(**options)


def provider(**options: Unpack[InjectableOptions]) -> Callable:
    """🐀 ⇝ decorator that marks a class as an injectable service"""
    return injectable(**options)
