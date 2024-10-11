from dataclasses import asdict
from typing import Any, Callable, Mapping, Type, TypeVar, Union

from ..metadata.meta import inject_metadata
from .protocols import DataclassInstance

Cls = TypeVar('Cls', bound=Type[Any])
Fn = TypeVar('Fn', bound=Callable[..., Any])


def meta(
    meta: Union[Mapping[str, Any], DataclassInstance]
) -> Callable[[Union[Cls, Fn]], Union[Cls, Fn]]:
    """🐀 » injects metadata into a class"""

    def decorator(callable: Union[Cls, Fn]) -> Union[Cls, Fn]:
        if isinstance(meta, Mapping):
            metadata = meta
        else:
            metadata = asdict(meta)

        inject_metadata(callable, metadata)
        return callable

    return decorator
