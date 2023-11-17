"""
Module providing typed dicts for the metadata HandlerMeta:
- pest/metadata/types/handler_meta.py

ATTENTION:
This file was auto-generated by tools/generator.py.
Do not edit manually.
"""

from enum import Enum
from typing import Any, Sequence, TypedDict

from fastapi import Response


class HandlerMetaDict(TypedDict, total=False):
    response_model: Any | None
    response_class: type[Response] | None
    status_code: int | None
    response_model_exclude_none: bool | None
    tags: list[str | Enum] | None
    dependencies: Sequence[Any] | None
    summary: str | None
    description: str | None
    deprecated: bool | None
    name: str | None
    responses: dict[int | str, dict[str, Any]] | None