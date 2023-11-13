from abc import ABC, abstractmethod

from pest.exceptions.base import PestException
from pest.metadata.types._meta import PestType
from pest.primitives.types.status import Status


class PestPrimitive(ABC):
    __class_status__: Status = Status.NOT_SETUP

    @property
    @classmethod
    @abstractmethod
    def __pest_object_type__(cls) -> PestType:
        """🐀 ⇝ returns the type of pest object"""
        ...


def status(
    clazz: type
) -> Status:
    """🐀 ⇝ gets a primitive's status"""
    if not issubclass(clazz, PestPrimitive):
        raise PestException(f'{clazz.__name__} is not a pest primitive.')

    return clazz.__class_status__
