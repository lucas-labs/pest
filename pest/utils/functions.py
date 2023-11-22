from typing import Any, TypedDict, TypeVar, cast

from pydantic import BaseModel

T = TypeVar('T', bound=dict)


def denone(x: T) -> T:
    """remove all keys with `None` values from a dictionary"""
    return cast(T, {k: v for k, v in x.items() if v is not None})


def clean_dict(d: dict[str, Any], type: type[TypedDict]) -> dict[str, Any]:
    """
    performs a cleaning operation on a dictionary to:
    1. remove all keys with `None` values
    2. keep only keys that are in the `TypedDict` type
    """
    return denone({k: v for k, v in d.items() if k in type.__annotations__})


def keep_keys(d: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    """keep only the specified keys in a dictionary"""
    return denone({k: v for k, v in d.items() if k in keys})


def drop_keys(d: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    """drop the specified keys from a dictionary"""
    return denone({k: v for k, v in d.items() if k not in keys})


def getset(d: dict, key: str, default: Any) -> Any:
    """get a value from a dictionary or set it if it does not exist, then return it"""
    if key not in d:
        d[key] = default
    return d[key]


def set_if_none(d: dict, key: str, value: Any) -> None:
    """set a value in a dictionary only if it does not exist on it already"""
    if key not in d:
        d[key] = value


def dump_model(model: BaseModel) -> dict[str, Any]:
    """dump a pydantic model to a dict

    HACK: this is a temporary function to support the new pydantic's model_dump() function
    while not breaking compatibility with pydantic@2x. This function works as a centralised
    way of future changes once pydantic<2 is dropped and model_dump() is the only
    function available. When that happens, this function will be removed and all calls to it
    will be replaced by `model.model_dump()`.
    """

    return (
        model.model_dump(exclude_none=True, exclude_unset=True)
        if hasattr(model, 'model_dump')
        else model.dict(exclude_none=True, exclude_unset=True)
    )
