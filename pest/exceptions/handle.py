from typing import Union

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, WebSocketRequestValidationError
from fastapi.utils import is_body_allowed_for_status_code
from fastapi.websockets import WebSocket
from pydantic import ValidationError
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.status import WS_1008_POLICY_VIOLATION

from ..utils.functions import dump_model
from .http.http import ExceptionResponse, PestHTTPException
from .http.status import HTTPStatusEnum, http_status


async def http(request: Request, exc: HTTPException) -> Response:
    """handles both `HTTPException` (fastapi) and `PestHTTPException` (pest)"""

    headers = getattr(exc, 'headers', None)
    if not is_body_allowed_for_status_code(exc.status_code):
        return Response(status_code=exc.status_code, headers=headers)

    if isinstance(exc, PestHTTPException):
        content = vars(exc)
    else:
        content = vars(
            PestHTTPException(
                status_code=exc.status_code,
                detail=exc.detail,
                headers=headers,
            )
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=headers,
    )


async def request_validation(
    request: Request, exc: Union[ValidationError, RequestValidationError]
) -> JSONResponse:
    """handles both `RequestValidationError` (fastapi) and `ValidationError` (pydantic)"""

    stat = http_status(HTTPStatusEnum.HTTP_400_BAD_REQUEST)

    messages = [
        f"{', '.join([str(elem) for elem in err['loc']])}: {err['msg'].capitalize()}"
        for err in exc.errors()
    ]

    return JSONResponse(
        status_code=stat.code,
        content=vars(ExceptionResponse(code=stat.code, error=stat.phrase, message=messages)),
    )


async def websocket_request_validation(
    websocket: WebSocket, exc: WebSocketRequestValidationError
) -> None:
    await websocket.close(code=WS_1008_POLICY_VIOLATION, reason=jsonable_encoder(exc.errors()))


async def the_rest(request: Request, exc: Exception) -> Response:
    """handles all other exceptions

    returns a generic 500 response and logs the exception message, just in case it
    was an
    """

    stat = http_status(HTTPStatusEnum.HTTP_500_INTERNAL_SERVER_ERROR)

    return JSONResponse(
        status_code=stat.code,
        content=dump_model(ExceptionResponse(code=stat.code, error=stat.phrase)),
    )
