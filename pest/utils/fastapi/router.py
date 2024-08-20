from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Set,
    Type,
    Union,
)

from fastapi import APIRouter, params
from fastapi.datastructures import Default, DefaultPlaceholder
from fastapi.routing import APIRoute
from fastapi.types import IncEx
from fastapi.utils import (
    generate_unique_id,
)
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute

if TYPE_CHECKING:  # pragma: no cover
    from ...core.controller import Controller


class PestRouter(APIRouter):
    """
    Extends the `APIRouter` class from FastAPI to handle / at the end of API routes.
    By default, FastAPI redirects routes that end in / to the route without /. This
    class avoids that behavior and for each route that is added, it adds an alternative
    route with or without /, as appropriate.
    """

    routes: List[APIRoute]
    controller: Type['Controller']

    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        response_model: Any = Default(None),
        status_code: Optional[int] = None,
        tags: Optional[List[Union[str, Enum]]] = None,
        dependencies: Optional[Sequence[params.Depends]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = 'Successful Response',
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        deprecated: Optional[bool] = None,
        methods: Optional[Union[Set[str], List[str]]] = None,
        operation_id: Optional[str] = None,
        response_model_include: Optional[IncEx] = None,
        response_model_exclude: Optional[IncEx] = None,
        response_model_by_alias: bool = True,
        response_model_exclude_unset: bool = False,
        response_model_exclude_defaults: bool = False,
        response_model_exclude_none: bool = False,
        include_in_schema: bool = True,
        response_class: Union[Type[Response], DefaultPlaceholder] = Default(JSONResponse),
        name: Optional[str] = None,
        route_class_override: Optional[Type[APIRoute]] = None,
        callbacks: Optional[List[BaseRoute]] = None,
        openapi_extra: Optional[Dict[str, Any]] = None,
        generate_unique_id_function: Union[Callable[[APIRoute], str], DefaultPlaceholder] = Default(
            generate_unique_id
        ),
        **kwargs: Any,
    ) -> None:
        """
        Registra un endpoint de la API con la ruta proporcionada y con su ruta alternativa
        dependiendo de si la ruta proporcionada termina en `/` o no.

        Por ejemplo, si se registra la ruta `/users`, se registrará también la ruta `/users/`
        y viceversa.
        """

        if path.endswith('/'):
            path = path[:-1]

        alternate_path = path + '/'

        if (self.prefix + path) != '':
            super().add_api_route(
                path,
                endpoint,
                response_model=response_model,
                status_code=status_code,
                tags=tags,
                dependencies=dependencies,
                summary=summary,
                description=description,
                response_description=response_description,
                responses=responses,
                deprecated=deprecated,
                methods=methods,
                operation_id=operation_id,
                response_model_include=response_model_include,
                response_model_exclude=response_model_exclude,
                response_model_by_alias=response_model_by_alias,
                response_model_exclude_unset=response_model_exclude_unset,
                response_model_exclude_defaults=response_model_exclude_defaults,
                response_model_exclude_none=response_model_exclude_none,
                include_in_schema=include_in_schema,
                response_class=response_class,
                name=name,
                route_class_override=route_class_override,
                callbacks=callbacks,
                openapi_extra=openapi_extra,
                generate_unique_id_function=generate_unique_id_function,
            )

        if (self.prefix + alternate_path) != '':
            super().add_api_route(
                alternate_path,
                endpoint,
                response_model=response_model,
                status_code=status_code,
                tags=tags,
                dependencies=dependencies,
                summary=summary,
                description=description,
                response_description=response_description,
                responses=responses,
                deprecated=deprecated,
                methods=methods,
                operation_id=operation_id,
                response_model_include=response_model_include,
                response_model_exclude=response_model_exclude,
                response_model_by_alias=response_model_by_alias,
                response_model_exclude_unset=response_model_exclude_unset,
                response_model_exclude_defaults=response_model_exclude_defaults,
                response_model_exclude_none=response_model_exclude_none,
                include_in_schema=False,
                response_class=response_class,
                name=name,
                route_class_override=route_class_override,
                callbacks=callbacks,
                openapi_extra=openapi_extra,
                generate_unique_id_function=generate_unique_id_function,
            )
