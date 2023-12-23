from typing import List, Sequence, Type, TypedDict, Union

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

from starlette.middleware import Middleware as StarletteMiddleware

from .base import PestMiddlwareCallback

MiddlewareDef: TypeAlias = Sequence[
    Union[StarletteMiddleware, Type[PestMiddlwareCallback], PestMiddlwareCallback]
]


class CorsOptions(TypedDict, total=False):
    allow_origins: List[str]
    '''
    Configures the `Access-Control-Allow-Origin`.

    Expects a list of origins that should be allowed to make cross-origin requests, or `"*"`
    to allow all origins.
    '''
    allow_methods: List[str]
    '''
    Configures the `Access-Control-Allow-Methods` header.

    Expects a list of allowed HTTP methods as strings, e.g. `["GET", "POST", "PUT", "DELETE"]`.
    Defaults to `["GET"]`
    '''
    allow_headers: List[str]
    '''
    Configures the `Access-Control-Allow-Headers` header.

    Expects a list of allowed HTTP headers as strings, e.g. `["Content-Type", "Authorization"]`.
    '''
    allow_credentials: bool
    '''
    Configures the `Access-Control-Allow-Credentials` header.

    Set to `True` to pass the header, otherwise it is omitted.
    '''
    allow_origin_regex: str
    '''
    Same as `allow_origins`, but expects a string that will be compiled to a regular expression
    object in order to match the origin.
    '''
    expose_headers: List[str]
    '''
    Configures the `Access-Control-Expose-Headers` header.

    Expects a list of HTTP headers as strings. If not specified, no custom headers are exposed.
    '''
    max_age: int
    '''
    Configures the `Access-Control-Max-Age` header.

    Expects an integer. Defaults to `600` (10 min).
    '''


DEFAULT_CORS_OPTIONS: CorsOptions = {
    'allow_methods': [
        'GET',
    ],
    'allow_credentials': False,
    'max_age': 600,
}
