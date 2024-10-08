from typing import Union

from dij import ActivationScope
from fastapi import Request, Response
from starlette.middleware.base import RequestResponseEndpoint

SCOPE_KEY = '__di_scope__'
'''🐀 ⇝ the key used to store the di activation scope in a request'''


def scope_from(request: Request) -> Union[ActivationScope, None]:
    """obtains the di activation scope from a request"""
    return getattr(request.state, SCOPE_KEY, None)


async def di_scope_middleware(request: Request, call_next: RequestResponseEndpoint) -> Response:
    """
    middleware that injects a di activation scope into the request. Allows the
    injection of request-scoped dependencies into controllers, services and other
    middlewares.
    """

    with ActivationScope() as scope:
        if scope.scoped_services is not None:
            setattr(request.state, SCOPE_KEY, scope)

        return await call_next(request)
