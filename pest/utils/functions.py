from typing import Any, TypedDict, TypeVar, cast

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
