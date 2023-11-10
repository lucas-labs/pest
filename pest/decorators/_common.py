
from typing import Any, Callable, Mapping, TypeVar

from dacite import Config, from_dict

from ..metadata.meta import inject_metadata
from ..metadata.types import Meta

T = TypeVar('T')
K = TypeVar('K')
Cls = TypeVar('Cls', bound=type[Any])


def singleton(cls: type[T]) -> type[T]:
    """
    makes the decorated class a singleton, ensuring
    that only one instance of the class is ever created.

    ```
    @singleton
    class MyClass: pass

    foo = MyClass()
    bar = MyClass()
    print(foo is bar)  # True
    ```
    """
    def constructor(cls: Any, *args: Any) -> T:
        instance = getattr(cls, '__instance__', None)
        if instance is None:
            instance = super(cls, cls).__new__(cls)
            setattr(cls, '__instance__', instance)
        return instance

    setattr(cls, '__new__', constructor)
    return cls


make_singleton = singleton


def _inject_class(
    base: type[T]
) -> Callable[..., type[T]]:
    return lambda cls: type(cls.__name__, (base,)+cls.__bases__, dict(cls.__dict__))


def mixin(
    base: type[T]
) -> Callable[..., type[T]]:
    """
    Utility decorator to inject a class as a mixin and combine it with the
    decorated class.

    The difference between this and `use_base` is that this
    decorator will cast the decorated class to the type of the base class.
    """
    return _inject_class(base=base)


def use_base(
    base: type
) -> Callable[[T], Callable[..., T]]:
    """
    Utility decorator to inject a class as a mixin and combine it with the
    decorated class.

    The difference between this and `mixin` is that this
    decorator will not cast the decorated class to the type of the base class.
    """
    return _inject_class(base=base)


def meta_decorator_mixin(
    meta_type: type[Meta],
    meta: Mapping[str, Any],
    base: type,
    singleton: bool = False,
) -> Callable[[Cls], type[Cls]]:
    """
    makes a decorator that sets the meta of a class
    and optionally makes it inherit from a base class
    """

    def wrapper(cls: Cls) -> type[Cls]:
        if singleton:
            cls = make_singleton(cls)

        inject_metadata(cls, from_dict(meta_type, meta, config=Config(check_types=False)))
        return mixin(base)(cls)

    return wrapper


def meta_decorator(
    meta_type: type[Meta],
    meta: Mapping[str, Any],
    base: type | None = None,
    singleton: bool = False,
) -> Callable:
    """
    makes a decorator that sets the meta of a class
    and optionally makes it inherit from a base class
    """

    def wrapper(cls: Cls) -> Callable[..., Cls]:
        if singleton:
            cls = make_singleton(cls)

        inject_metadata(cls, from_dict(meta_type, meta, config=Config(check_types=False)))
        return use_base(base)(cls) if base is not None else cls

    return wrapper
