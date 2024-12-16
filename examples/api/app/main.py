import re
from typing import Any

from fastapi import Request, Response
from starlette.datastructures import MutableHeaders
from starlette.middleware import Middleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from pest import Pest
from pest.di import inject
from pest.logging import LogLevel

from .app_module import AppModule
from .data.data import TodoRepo


async def pest_middleware(
    request: Request,
    call_next: RequestResponseEndpoint,
    # inject() is just a dummy function, it doesn't do anything
    # it's just there for type checking, otherwise my_middleware wouldn't be
    # considered a valid middleware function (needs a default value for the
    # Protocol to be "respected"). Might be changed in the future.
    repo: TodoRepo = inject(),  # injection works in middleware too!
) -> Response:
    response = await call_next(request)
    response.headers['X-Process-Time-1'] = repo.now()
    return response


class PureAsgiMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        # injection has not been implemented for pure asgi middlewares (yet)
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)

        async def send_wrapper(message: Message) -> None:
            if message['type'] == 'http.response.start':
                headers = MutableHeaders(scope=message)
                headers.append('X-Process-Time-2', '0.5')
            await send(message)

        await self.app(scope, receive, send_wrapper)


def format_record(record: Any) -> str:
    # strip ANSI escape sequences
    format_string = '<green>{time}</green> <level>{message}</level>\n'
    ansi_escape = re.compile(r'\x1B\[\d+(;\d+){0,2}m')
    record['message'] = ansi_escape.sub('', record['message'])
    return format_string


app = Pest.create(
    AppModule,
    logging={
        'intercept': [('uvicorn*', LogLevel.DEBUG), 'pest*', 'fastapi'],
        'level': LogLevel.DEBUG,
        # 'format': format_record,
        'access_log': True,
        'sinks': [{'sink': 'examples/logs/app.log', 'rotation': '1 week', 'format': format_record}],
    },
    middleware=[Middleware(PureAsgiMiddleware), pest_middleware],
    cors={
        'allow_origins': ['*'],
    },
)


# fastapi's middleware decorator is also supported
@app.middleware('http')
async def fastapi_middleware(
    request: Request,
    call_next: RequestResponseEndpoint,
    repo: TodoRepo,  # but we can inject stuff now too!
) -> Response:
    response = await call_next(request)
    response.headers['X-Process-Time-3'] = repo.now()
    return response
