"""
Module providing typed dicts for the metadata ControllerMeta:
- pest/metadata/types/controller_meta.py

ATTENTION:
This file was auto-generated by `task gen:types`.
Do not edit manually.
"""

from enum import Enum
from typing import Any, Callable, Sequence, TypedDict


class ControllerMetaDict(TypedDict, total=False):
    tags: list[str | Enum] | None
    '''🐀 ⇝ tags of the controller'''

    redirect_slashes: bool | None
    '''🐀 ⇝ redirect slashes?'''

    on_startup: Sequence[Callable[[], Any]] | None
    '''🐀 ⇝ on startup events'''

    on_shutdown: Sequence[Callable[[], Any]] | None
    '''🐀 ⇝ lifespan of the controller'''

    deprecated: bool | None
    '''🐀 ⇝ is the controller deprecated?'''

    include_in_schema: bool | None
    '''🐀 ⇝ include in schema?'''

