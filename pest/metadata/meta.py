from dataclasses import asdict, fields, is_dataclass
from typing import Any, Callable, Dict, List, Mapping, Type, TypeVar, Union, cast

from dacite import Config, from_dict

from ..exceptions.base.pest import PestException
from ..utils.functions import drop_keys, keep_keys
from ..utils.protocols import DataclassInstance
from .types._meta import Meta

META_KEY = '__pest__'


DataType = TypeVar('DataType', bound=Union[Dict[str, Any], dict, Meta, DataclassInstance])
GenericValue = TypeVar('GenericValue')


def get_meta(
    target: Union[Callable[..., Any], type, object],
    output_type: Type[DataType] = Dict[str, Any],
    *,
    raise_error: bool = True,
    clean: bool = False,
    keep: Union[List[str], None] = None,
    drop: Union[List[str], None] = None,
) -> DataType:
    """🐀 ⇝ get `metadata` from a `callable`
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

    if is_dataclass(output_type):
        return cast(output_type, from_dict(output_type, meta, config=Config(check_types=False)))  # type: ignore

    return cast(output_type, meta)  # type: ignore


def get_meta_value(
    callable: Callable[..., Any],
    key: str,
    default: Any = None,
    *,
    type: Type[GenericValue] = Type[Any],
) -> GenericValue:
    """🐀 ⇝ get pest metadata `value` from a `callable` by `key`"""

    meta = get_meta(callable, raise_error=False)
    return cast(type, meta.get(key, default))  # type: ignore


def inject_metadata(
    callable: Callable[..., Any],
    metadata: Union[Meta, Mapping[Any, Any], None] = None,
    **kwargs: Any,
) -> None:
    """🐀 ⇝ initialize pest `metadata` for a `callable`

    callable: The callable to initialize metadata for
    **kwargs: keyword arguments to initialize metadata with
    """

    if not hasattr(callable, META_KEY):
        setattr(callable, META_KEY, {})

    dict_meta = {}
    if metadata is not None:
        if not is_dataclass(metadata) and not isinstance(metadata, dict):
            raise PestException('metadata must be a dataclass or a dict')

        try:
            dict_meta: dict = (
                asdict(metadata)
                if is_dataclass(metadata) and not isinstance(metadata, type)
                else metadata if isinstance(metadata, dict) else {}
            )
        except Exception as e:
            if is_dataclass(metadata) and not isinstance(metadata, type):
                dict_meta = {}
                for field in fields(metadata):
                    dict_meta[field.name] = getattr(metadata, field.name)
            else:
                raise e

    meta = get_meta(callable)
    meta.update({**dict_meta, **kwargs})
