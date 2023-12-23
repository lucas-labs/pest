from abc import ABC, abstractmethod
from inspect import isclass
from typing import Union

from ...utils.functions import classproperty

try:
    from typing import TypeGuard
except ImportError:
    from typing_extensions import TypeGuard

from pest.metadata.types._meta import PestType

from ...exceptions.base.pest import PestException
from ..types.status import Status


class PestPrimitive(ABC):
    __class_status__: Status = Status.NOT_SETUP

    @classproperty
    @abstractmethod
    def __pest_object_type__(cls) -> PestType:
        """🐀 ⇝ returns the type of pest object"""
        ...


def is_primitive(clazz: Union[type, object]) -> TypeGuard[PestPrimitive]:
    """🐀 ⇝ checks if a class is a pest primitive"""
    if not isclass(clazz):
        return isinstance(clazz, PestPrimitive)

    return issubclass(clazz, PestPrimitive)


def status(clazz: Union[type, object]) -> Status:
    """🐀 ⇝ gets a primitive's status"""
    is_class = isclass(clazz)
    name = clazz.__name__ if is_class else clazz.__class__.__name__
    if not is_primitive(clazz):
        raise PestException(f'{name} is not a pest primitive.')

    if is_class:
        return getattr(clazz, '__class_status__', Status.NOT_SETUP)

    return clazz.__class_status__


def primitive_type(clazz: Union[type, object]) -> PestType:
    """🐀 ⇝ gets a primitive's type"""
    is_class = isclass(clazz)
    name = clazz.__name__ if is_class else clazz.__class__.__name__

    if not is_primitive(clazz):
        raise PestException(f'{name} is not a pest primitive.')
    if is_class:
        return getattr(clazz, '__pest_object_type__')

    return clazz.__pest_object_type__
