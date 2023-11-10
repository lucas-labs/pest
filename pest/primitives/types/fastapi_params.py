from typing import (
    Any,
    Callable,
    Coroutine,
    Self,
    Sequence,
    TypedDict,
)

from fastapi import Request, Response
from fastapi.middleware import Middleware
from fastapi.params import Depends
from fastapi.routing import APIRouter
from starlette.routing import BaseRoute
from starlette.types import Lifespan


class FastAPIParams(TypedDict, total=False):
    debug: bool
    routes: list[BaseRoute]
    title: str
    summary: str
    description: str
    version: str
    openapi_url: str
    openapi_tags: list[dict[str, Any]]
    servers: list[dict[str, str | Any]]
    dependencies: Sequence[Depends]
    default_response_class: type[Response]
    redirect_slashes: bool
    docs_url: str
    redoc_url: str
    swagger_ui_oauth2_redirect_url: str
    swagger_ui_init_oauth: dict[str, Any]
    middleware: Sequence[Middleware]
    exception_handlers: dict[
        int | type[Exception],
        Callable[[Request, Any], Coroutine[Any, Any, Response]],
    ]
    on_startup: Sequence[Callable[[], Any]]
    on_shutdown: Sequence[Callable[[], Any]]
    lifespan: Lifespan[Self]
    terms_of_service: str
    contact: dict[str, str | Any]
    license_info: dict[str, str | Any]
    openapi_prefix: str
    root_path: str
    root_path_in_servers: bool
    responses: dict[int | str, dict[str, Any]]
    callbacks: list[BaseRoute]
    webhooks: APIRouter
    deprecated: bool
    include_in_schema: bool
    swagger_ui_parameters: dict[str, Any]
    separate_input_output_schemas: bool
