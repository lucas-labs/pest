from typing import Any, Dict, List, Union

from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException

from ...utils.functions import dump_model
from .status import http_status


class ExceptionResponse(BaseModel):
    """Error response model"""

    code: int = Field(..., description='HTTP status code')
    error: Union[str, None] = Field(default=None, description='HTTP status phrase')
    message: Union[List[str], str, None] = Field(default=None, description='Error message')

    @staticmethod
    def example(code: int) -> 'ExceptionResponse':
        status = http_status(code)

        return ExceptionResponse(
            code=status.code,
            error=status.phrase,
            message='Detailed error message',
        )


def exc_response(*codes: int) -> Dict[Union[int, str], Dict[str, Any]]:
    """🐀 ⇝ Generate a dict of error responses for the given status codes for use in OpenAPI docs"""

    responses = {}

    for code in codes:
        example = ExceptionResponse.example(code)
        responses[code] = {
            'description': example.error,
            'model': ExceptionResponse,
            'content': {
                'application/json': {
                    'example': example.model_dump(),
                },
            },
        }

    return responses


class PestHTTPException(HTTPException):
    """🐀 ⇝ base class for all pest HTTP exceptions"""

    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers,
        )

    @property
    def __dict__(self) -> Dict[str, Any]:
        status = http_status(self.status_code)

        return dump_model(
            ExceptionResponse(code=status.code, error=status.phrase, message=self.detail)
        )


# region: HTTP 4xx errors
class BadRequestException(PestHTTPException):
    """🐀 ⇝ `400` Bad Request

    The server cannot or will not process the request due to something that is perceived to be
    a client error (e.g., malformed request syntax, invalid request message framing, or deceptive
    request routing).

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `400` Bad Request"""
        super().__init__(
            status_code=400,
            detail=detail,
            headers=headers,
        )


class UnauthorizedException(PestHTTPException):
    """🐀 ⇝ `401` Unauthorized

    Similar to `403 Forbidden`, but specifically for use when authentication is required and has
    failed or has not yet been provided. It indicates that the client must authenticate
    itself to get the requested response.

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/401)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `401` Unauthorized"""
        super().__init__(
            status_code=401,
            detail=detail,
            headers=headers,
        )


class ForbiddenException(PestHTTPException):
    """🐀 ⇝ `403` Forbidden

    The client does not have access rights to the content; that is, it is unauthorized,
    so the server is refusing to give the requested resource. Unlike `401`, the client's
    identity is known to the server.

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `403` Forbidden"""
        super().__init__(
            status_code=403,
            detail=detail,
            headers=headers,
        )


class NotFoundException(PestHTTPException):
    """🐀 ⇝ `404` Not Found

    The requested resource could not be found but may be available in the future.

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `404` Not Found"""
        super().__init__(
            status_code=404,
            detail=detail,
            headers=headers,
        )


class MethodNotAllowedException(PestHTTPException):
    """🐀 ⇝ `405` Method Not Allowed

    A request method is not supported for the requested resource; for example, an API endpoint
    may not support `DELETE` requests.

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/405)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `405` Method Not Allowed"""
        super().__init__(
            status_code=405,
            detail=detail,
            headers=headers,
        )


class NotAcceptableException(PestHTTPException):
    """🐀 ⇝ `406` Not Acceptable

    The requested resource is capable of generating only content not acceptable according to the
    Accept headers sent in the request.

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/406)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `406` Not Acceptable"""
        super().__init__(
            status_code=406,
            detail=detail,
            headers=headers,
        )


class ProxyAuthenticationRequiredException(PestHTTPException):
    """🐀 ⇝ `407` Proxy Authentication Required

    This is similar to 401 Unauthorized but authentication is needed to be done by a proxy.

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/407)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
        headers_: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `407` Proxy Authentication Required"""
        super().__init__(
            status_code=407,
            detail=detail,
            headers=headers,
        )
        self.headers = headers_


class RequestTimeoutException(PestHTTPException):
    """🐀 ⇝ `408` Request Timeout

    The server timed out waiting for the request.

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/408)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `408` Request Timeout"""
        super().__init__(
            status_code=408,
            detail=detail,
            headers=headers,
        )


class ConflictException(PestHTTPException):
    """🐀 ⇝ `409` Conflict

    Indicates that the request could not be processed because of conflict in the request, such as
    an attempt to modify a resource in a way that would conflict with its current state.

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/409)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `409` Conflict"""
        super().__init__(
            status_code=409,
            detail=detail,
            headers=headers,
        )


class GoneException(PestHTTPException):
    """🐀 ⇝ `410` Gone

    This response is sent when the requested content has been permanently deleted from server.

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/410)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `410` Gone"""
        super().__init__(
            status_code=410,
            detail=detail,
            headers=headers,
        )


class PreconditionFailedException(PestHTTPException):
    """🐀 ⇝ `412` Precondition Failed

    The client has indicated preconditions in its headers which the server does not meet.

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/412)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `412` Precondition Failed"""
        super().__init__(
            status_code=412,
            detail=detail,
            headers=headers,
        )


class PayloadTooLargeException(PestHTTPException):
    """🐀 ⇝ `413` Payload Too Large

    Request entity is larger than limits defined by server. The server might close the
    connection or return an Retry-After header field.

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/413)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `413` Payload Too Large"""
        super().__init__(
            status_code=413,
            detail=detail,
            headers=headers,
        )


class UnsupportedMediaTypeException(PestHTTPException):
    """🐀 ⇝ `415` Unsupported Media Type

    The media format of the requested data is not supported by the server, so the
    server is rejecting the request

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/415)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
        media_type: Union[str, None] = None,
    ) -> None:
        """🐀 ⇝ `415` Unsupported Media Type"""
        super().__init__(
            status_code=415,
            detail=detail,
            headers=headers,
        )
        self.media_type = media_type


class ImATeapotException(PestHTTPException):
    """🐀 ⇝ `418` I'm a teapot

    The server was asked to brew coffee but it can't because it is, permanently, a teapot.

    🤪

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/418)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `418` I'm a teapot"""
        super().__init__(
            status_code=418,
            detail=detail,
            headers=headers,
        )


class UnprocessableEntityException(PestHTTPException):
    """🐀 ⇝ `422` Unprocessable Entity

    The request was well-formed but was unable to be followed due to semantic errors.

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/422)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `422` Unprocessable Entity"""
        super().__init__(
            status_code=422,
            detail=detail,
            headers=headers,
        )


# endregion


# region: HTTP 5xx errors
class InternalServerErrorException(PestHTTPException):
    """🐀 ⇝ `500` Internal Server Error

    A generic error message, given when an unexpected condition was encountered and no more
    specific message is suitable or available.

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `500` Internal Server Error"""
        super().__init__(
            status_code=500,
            detail=detail,
            headers=headers,
        )


class NotImplementedException(PestHTTPException):
    """🐀 ⇝ `501` Not Implemented

    The request method is not supported by the server and cannot be handled.

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/501)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `501` Not Implemented"""
        super().__init__(
            status_code=501,
            detail=detail,
            headers=headers,
        )


class BadGatewayException(PestHTTPException):
    """🐀 ⇝ `502` Bad Gateway

    This error response means that the server, while working as a gateway to get a response
    needed to handle the request, got an invalid response.

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/502)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `502` Bad Gateway"""
        super().__init__(
            status_code=502,
            detail=detail,
            headers=headers,
        )


class ServiceUnavailableException(PestHTTPException):
    """🐀 ⇝ `503` Service Unavailable

    The server is not ready to handle the request for some reason.

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/503)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `503` Service Unavailable"""
        super().__init__(
            status_code=503,
            detail=detail,
            headers=headers,
        )


class GatewayTimeoutException(PestHTTPException):
    """🐀 ⇝ `504` Gateway Timeout

    This error response is given when the server is acting as a gateway and cannot get
    a response in time.

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/504)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `504` Gateway Timeout"""
        super().__init__(
            status_code=504,
            detail=detail,
            headers=headers,
        )


class HttpVersionNotSupportedException(PestHTTPException):
    """🐀 ⇝ `505` HTTP Version Not Supported

    The HTTP version used in the request is not supported by the server.

    [› more](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/505)
    """

    def __init__(
        self,
        detail: Any = None,
        headers: Union[Dict[str, Any], None] = None,
    ) -> None:
        """🐀 ⇝ `505` HTTP Version Not Supported"""
        super().__init__(
            status_code=505,
            detail=detail,
            headers=headers,
        )


# endregion
