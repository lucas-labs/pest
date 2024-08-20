from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Sequence,
    Type,
    TypedDict,
    Union,
)

from fastapi import FastAPI, Request, Response
from fastapi.params import Depends
from fastapi.routing import APIRouter
from starlette.routing import BaseRoute
from starlette.types import Lifespan


class FastAPIParams(TypedDict, total=False):
    debug: bool
    routes: List[BaseRoute]
    title: str
    summary: str
    description: str
    version: str
    openapi_url: str
    openapi_tags: List[Dict[str, Any]]
    servers: List[Dict[str, Union[str, Any]]]
    dependencies: Sequence[Depends]
    default_response_class: Type[Response]
    redirect_slashes: bool
    docs_url: str
    redoc_url: str
    swagger_ui_oauth2_redirect_url: str
    swagger_ui_init_oauth: Dict[str, Any]
    exception_handlers: Dict[
        Union[int, Type[Exception]],
        Callable[[Request, Any], Coroutine[Any, Any, Response]],
    ]
    on_startup: Sequence[Callable[[], Any]]
    on_shutdown: Sequence[Callable[[], Any]]
    lifespan: Lifespan[FastAPI]
    terms_of_service: str
    contact: Dict[str, Union[str, Any]]
    license_info: Dict[str, Union[str, Any]]
    openapi_prefix: str
    root_path: str
    root_path_in_servers: bool
    responses: Dict[Union[int, str], Dict[str, Any]]
    callbacks: List[BaseRoute]
    webhooks: APIRouter
    deprecated: bool
    include_in_schema: bool
    swagger_ui_parameters: Dict[str, Any]
    separate_input_output_schemas: bool
