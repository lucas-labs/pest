from enum import Enum
from typing import (
    Annotated,
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    Union,
    Unpack,
)

from fastapi import FastAPI, Response, routing
from fastapi.datastructures import Default, DefaultPlaceholder
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from fastapi.types import DecoratedCallable, IncEx
from fastapi.utils import generate_unique_id
from rodi import ActivationScope
from starlette.middleware import Middleware
from starlette.routing import BaseRoute
from typing_extensions import Doc

from pest.logging import log
from pest.middleware.types import CorsOptions

from ..metadata.types.module_meta import InjectionToken
from ..middleware.base import (
    PestBaseHTTPMiddleware,
)
from ..middleware.types import MiddlewareDef
from .module import Module, T
from .types.fastapi_params import FastAPIParams


def root_module(app: 'PestApplication') -> Module:
    return app.__pest_module__


class PestApplication(FastAPI):
    """🐀 ⇝ what a pest!"""

    def __init__(
        self, module: Module, middleware: MiddlewareDef, **kwargs: Unpack[FastAPIParams]
    ) -> None:
        super().__init__(**kwargs)
        self.__pest_module__ = module

        self.user_middleware: List[Middleware] = (
            [] if middleware is None else [
                middleware
                if isinstance(middleware, Middleware)
                else Middleware(PestBaseHTTPMiddleware, dispatch=middleware, provideFn=self.resolve)
                for middleware in middleware
            ]
        )
        print('ok')

    def __str__(self) -> str:
        return str(root_module(self))

    def resolve(self, token: InjectionToken[T], scope: ActivationScope | None = None) -> T:
        return root_module(self).get(token, scope)

    def can_provide(self, token: InjectionToken[T]) -> bool:
        return root_module(self).can_provide(token)

    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Coroutine[Any, Any, Response]],
        *,
        response_model: Any = Default(None),
        status_code: Optional[int] = None,
        tags: Optional[List[Union[str, Enum]]] = None,
        dependencies: Optional[Sequence[Depends]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = 'Successful Response',
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        deprecated: Optional[bool] = None,
        methods: Optional[List[str]] = None,
        operation_id: Optional[str] = None,
        response_model_include: Optional[IncEx] = None,
        response_model_exclude: Optional[IncEx] = None,
        response_model_by_alias: bool = True,
        response_model_exclude_unset: bool = False,
        response_model_exclude_defaults: bool = False,
        response_model_exclude_none: bool = False,
        include_in_schema: bool = True,
        response_class: Union[Type[Response], DefaultPlaceholder] = Default(
            JSONResponse
        ),
        name: Optional[str] = None,
        openapi_extra: Optional[Dict[str, Any]] = None,
        generate_unique_id_function: Callable[[routing.APIRoute], str] = Default(
            generate_unique_id
        ),
        **kwargs: Any,
    ) -> None:
        self.router.add_api_route(
            path,
            endpoint=endpoint,
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
            openapi_extra=openapi_extra,
            generate_unique_id_function=generate_unique_id_function,
            **kwargs,
        )

    def include_router(
        self,
        router: routing.APIRouter,
        *,
        prefix: str = '',
        tags: Optional[List[Union[str, Enum]]] = None,
        dependencies: Optional[Sequence[Depends]] = None,
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        default_response_class: Type[Response] = Default(JSONResponse),
        callbacks: Optional[List[BaseRoute]] = None,
        generate_unique_id_function: Callable[[routing.APIRoute], str] = Default(
            generate_unique_id
        ),
    ) -> None:
        self.router.include_router(
            router,
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
            responses=responses,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            default_response_class=default_response_class,
            callbacks=callbacks,
            generate_unique_id_function=generate_unique_id_function,
        )

    def middleware(
        self,
        middleware_type: Annotated[
            str,
            Doc(
                '''
                The type of middleware. Currently only supports `http`.
                '''
            ),
        ],
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """
        Add a middleware to the application.

        Read more about it in the
        [FastAPI docs for Middleware](https://fastapi.tiangolo.com/tutorial/middleware/).

        ## Example

        ```python
        import time

        from fastapi import FastAPI, Request

        app = FastAPI()


        @app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response
        ```
        """

        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            self.add_middleware(PestBaseHTTPMiddleware, dispatch=func, provideFn=self.resolve)
            return func

        return decorator

    def enable_cors(self, **opts: Unpack[CorsOptions]) -> None:
        from starlette.middleware.cors import CORSMiddleware

        from ..middleware.types import DEFAULT_CORS_OPTIONS

        log.debug(f'Enabling CORS with options: {DEFAULT_CORS_OPTIONS | opts}')

        self.add_middleware(CORSMiddleware, **opts)
