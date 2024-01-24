from dataclasses import Field
from typing import ClassVar, Dict, Protocol


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[Dict[str, Field]]
