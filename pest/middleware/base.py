
import functools
from inspect import Signature, isclass, isfunction
from typing import (
    Any,
    Callable,
    Optional,
    Protocol,
    TypeAlias,
    TypeGuard,
    runtime_checkable,
)

from rodi import ActivationScope
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    DispatchFunction,
    RequestResponseEndpoint,
    T,
)
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from ..metadata.types.module_meta import InjectionToken
from .di import scope_from

ProvideFn: TypeAlias = Callable[[InjectionToken[T], Optional[ActivationScope]], T]


@runtime_checkable
class PestMwDispatcher(Protocol):
    async def __call__(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        ...


class PestBaseHTTPMiddleware(BaseHTTPMiddleware):
    """🐀 ⇝ asgi middleware that receivs an injetor function and a dispatch funtion

    same as `starlette`'s `BaseHTTPMiddleware` but this one supports receiving injection
    """

    def __init__(
        self,
        app: ASGIApp,
        provideFn: ProvideFn,
        dispatch: PestMwDispatcher
    ) -> None:
        self.provide = provideFn
        super().__init__(app, dispatch=self.__dispatch_fn(dispatch))

    def __dispatch_fn(self, dispatch: PestMwDispatcher) -> DispatchFunction | None:
        if dispatch is None:
            return dispatch

        @functools.wraps(dispatch)
        async def dispatch_fn(request: Request, call_next: RequestResponseEndpoint) -> Response:
            scope = scope_from(request)
            args, kwargs = self.__resolve_args(dispatch, scope)
            return await dispatch(request, call_next, *args, **kwargs)

        return dispatch_fn

    def __resolve_args(self, function: DispatchFunction, scope: ActivationScope | None) -> tuple[tuple, dict]:
        signature = Signature.from_callable(function)
        parameters = signature.parameters
        args = []
        kwargs = {}

        arg_count = 0
        for name, param in parameters.items():
            if arg_count < 2:
                arg_count += 1
                continue

            if param.kind == param.POSITIONAL_ONLY or param.kind == param.POSITIONAL_OR_KEYWORD:
                args.append(self.provide(param.annotation, scope))

            elif param.kind == param.KEYWORD_ONLY:
                kwargs[name] = self.provide(param.annotation, scope)

        return tuple(args), kwargs


def inject() -> Any:
    """🐀 ⇝ placeholder to indicate that a parameter should be injected"""
    ...


def is_pest_dispatcher(obj: Any) -> TypeGuard[PestMwDispatcher]:
    respects_protocol = (
        isclass(obj) and issubclass(obj, PestMwDispatcher) or
        callable(obj) and isinstance(obj, PestMwDispatcher)
    )

    if not respects_protocol:
        return False

    # Check the function signature
    is_function = isfunction(obj)
    fn = obj if is_function else obj.__call__
    params = Signature.from_callable(fn).parameters
    args = list(params) if is_function else list(params)[1:]

    # Check if the first two arguments are 'request' and 'call_next'
    if args[:2] != ['request', 'call_next']:
        return False

    return True
