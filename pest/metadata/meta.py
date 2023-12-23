from dataclasses import asdict, is_dataclass
from typing import Any, Callable, Dict, List, Type, TypeVar, Union, cast

from dacite import Config, from_dict

from ..exceptions.base.pest import PestException
from ..utils.functions import drop_keys, keep_keys
from .types._meta import Meta

META_KEY = '__pest__'


DataType = TypeVar('DataType', bound=Union[Dict[str, Any], dict, Meta])
GenericValue = TypeVar('GenericValue')


def get_meta(
    target: Union[Callable[..., Any], type, object],
    *,
    type: Type[DataType] = Dict[str, Any],
    raise_error: bool = True,
    clean: bool = False,
    keep: Union[List[str], None] = None,
    drop: Union[List[str], None] = None,
) -> DataType:
    """🐀 ⇝ get pest `metadata` from a `callable`
    #### Params
    - target: target object, type or function
    - type: return type (will create an instance if it's a `dataclass`)
    - raise_error: wether to raise an error if no metadata was found in the target
    - clean: wether to clean up the resulting object (will remove `meta_type` by default)
    - keep: if `clean == True`, will only keep the key the keys provided here
    - drop: if `clean == True`, will drop all keys provided here and keep the rest.
    """

    if not hasattr(target, META_KEY):
        if raise_error:
            raise PestException(f'No metadata for {target}')
        return cast(DataType, {})

    meta = getattr(target, META_KEY)

    # clean up the metadata
    if clean:
        if keep is not None and len(keep) > 0:
            meta = keep_keys(meta, keep)

        if drop is not None and len(drop) > 0:
            meta = drop_keys(meta, drop)

        if not keep and not drop:
            meta = drop_keys(meta, ['meta_type'])

    if is_dataclass(type):
        return cast(type, from_dict(type, meta, config=Config(check_types=False)))

    return cast(type, meta)


def get_meta_value(
    callable: Callable[..., Any], key: str, default: Any = None, *, type: Type[GenericValue] = Any
) -> GenericValue:
    """🐀 ⇝ get pest metadata `value` from a `callable` by `key`"""

    meta = get_meta(callable, raise_error=False)
    return cast(type, meta.get(key, default))


def inject_metadata(
    callable: Callable[..., Any], metadata: Union[Meta, None] = None, **kwargs: Any
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
            raise PestException('metadata must be a dataclass')
        dict_meta = asdict(metadata)

    meta = get_meta(callable)
    meta.update({**dict_meta, **kwargs})
