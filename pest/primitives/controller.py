
from abc import ABC

from ..metadata.types._meta import MetaType


class Controller(ABC):
    __pest_object_type__ = MetaType.CONTROLLER
