from dataclasses import asdict
from typing import Any, Callable, Mapping, Type, TypeVar, Union

from ..metadata.meta import inject_metadata
from .protocols import DataclassInstance

Cls = TypeVar('Cls', bound=Type[Any])


def meta(meta: Union[Mapping[str, Any], DataclassInstance]) -> Callable[[Cls], Cls]:
    """🐀 » injects metadata into a class"""

    def wrapper(cls: Cls) -> Cls:
        if isinstance(meta, Mapping):
            metadata = meta
        else:
            metadata = asdict(meta)

        inject_metadata(cls, metadata)
        return cls

    return wrapper
