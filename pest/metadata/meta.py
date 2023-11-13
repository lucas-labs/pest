from dataclasses import asdict, is_dataclass
from typing import Any, Callable, TypedDict, TypeVar, Union, cast

from dacite import Config, from_dict

from .types._meta import Meta

META_KEY = '__pest__'


DataType = TypeVar('DataType', bound=Union[dict[str, Any], TypedDict, Meta])
GenericValue = TypeVar('GenericValue')


def get_meta(
    callable: Callable[..., Any] | type | object,
    *,
    type: type[DataType] = dict[str, Any],
    raise_error: bool = True
) -> DataType:
    """🐀 ⇝ get pest `metadata` from a `callable`"""

    if not hasattr(callable, META_KEY):
        if raise_error:
            raise ValueError(f'No metadata for {callable}')
        return cast(DataType, {})

    meta = getattr(callable, META_KEY)

    if is_dataclass(type):
        return cast(type, from_dict(type, meta, config=Config(check_types=False)))

    return cast(type, meta)


def get_meta_value(
    callable: Callable[..., Any],
    key: str,
    default: Any = None,
    *,
    type: type[GenericValue] = Any
) -> GenericValue:
    """🐀 ⇝ get pest metadata `value` from a `callable` by `key`"""

    meta = get_meta(callable, raise_error=False)
    return cast(type, meta.get(key, default))


def inject_metadata(
    callable: Callable[..., Any],
    metadata: Meta | None = None,
    **kwargs: Any
) -> None:
    """🐀 ⇝ initialize pest `metadata` for a `callable`

    callable: The callable to initialize metadata for
    **kwargs: keyword arguments to initialize metadata with
    """

    if not hasattr(callable, META_KEY):
        setattr(callable, META_KEY, {})

    dict_meta = {}
    if metadata is not None:
        if not is_dataclass(metadata):
            raise TypeError('metadata must be a dataclass')
        dict_meta = asdict(metadata)

    meta = get_meta(callable)
    meta.update({**dict_meta, **kwargs})
