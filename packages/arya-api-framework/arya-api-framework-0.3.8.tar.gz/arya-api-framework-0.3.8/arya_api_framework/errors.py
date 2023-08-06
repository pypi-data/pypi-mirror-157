"""
Author: Arya Mayfield
Date: June 2022
Description: Various exceptions for use throughout the module.
"""

# Stdlib modules
from typing import (
    Any,
    Optional,
    Union,
)

# 3rd party modules
from pydantic import BaseModel

# Local modules
from .constants import HTTPStatus

# Define exposed objects
__all__ = [
    # General
    "ValidationError",
    "ExtensionError",
    "ExtensionNotFound",
    "ExtensionAlreadyLoaded",
    "ExtensionNotLoaded",
    "ExtensionEntryPointError",
    "ExtensionFailed",
    # Client
    "ClientError",
    "AsyncClientError",
    "SyncClientError",
    "SubClientError",
    "SubClientAlreadyLoaded",
    "SubClientParentSet",
    "SubClientNotLoaded",
    # Requests
    "ResponseParseError",
    'HTTPError',
    'HTTPRedirect',
    'HTTPClientError',
    'HTTPServerError',
    # 300
    'HTTPMultipleChoices',
    'HTTPMovedPermanently',
    'HTTPFound',
    'HTTPSeeOther',
    'HTTPNotModified',
    'HTTPUseProxy',
    'HTTPReserved',
    'HTTPTemporaryRedirect',
    'HTTPPermanentRedirect',
    # 400
    'HTTPBadRequest',
    'HTTPUnauthorized',
    'HTTPPaymentRequired',
    'HTTPForbidden',
    'HTTPNotFound',
    'HTTPMethodNotAllowed',
    'HTTPNotAcceptable',
    'HTTPProxyAuthenticationRequired',
    'HTTPRequestTimeout',
    'HTTPConflict',
    'HTTPGone',
    'HTTPLengthRequired',
    'HTTPPreconditionFailed',
    'HTTPRequestEntityTooLarge',
    'HTTPRequestUriTooLong',
    'HTTPUnsupportedMediaType',
    'HTTPRequestedRangeNotSatisfiable',
    'HTTPExpectationFailed',
    'HTTPImATeapot',
    'HTTPMisdirectedRequest',
    'HTTPUnprocessableEntity',
    'HTTPFailedDependency',
    'HTTPTooEarly',
    'HTTPUpgradeRequired',
    'HTTPPreconditionRequired',
    'HTTPTooManyRequests',
    'HTTPRequestHeaderFieldsTooLarge',
    'HTTPUnavailableForLegalReasons',
    # 500
    'HTTPInternalServerError',
    'HTTPNotImplemented',
    'HTTPBadGateway',
    'HTTPServiceUnavailable',
    'HTTPGatewayTimeout',
    'HTTPHttpServerVersionNotSupported',
    'HTTPVariantAlsoNegotiates',
    'HTTPInsufficientStorage',
    'HTTPLoopDetected',
    'HTTPNotExtended',
    'HTTPNetworkAuthenticationRequired',
    # Definitions
    'ERROR_RESPONSE_MAPPING',
]

# ======================
#        Typing
# ======================
Response = Union[str, bytes, dict, list, BaseModel]
RawResponse = Union[str, bytes]


# ======================
#   Generalized Errors
# ======================
class FrameworkException(Exception):
    """
    The core exception for all exceptions used in the API framework.
    """
    pass


class ValidationError(FrameworkException):
    """
    .. inherits_from:: FrameworkException

    Raised when validating a variable's type.
    """
    pass


class ExtensionError(FrameworkException):
    """
    .. inherits_from:: FrameworkException

    The base exception for errors related to extensions.

    Attributes
    ----------
        name: :py:class:`str`
            The extension that had an error.
    """
    name: str

    def __init__(self, message: Optional[str] = None, *args: Any, name: str) -> None:
        self.name = name
        message = message or f'Extension {name!r} has en error.'
        super().__init__(message, *args)


class ExtensionNotFound(ExtensionError):
    """
    .. inherits_from:: ExtensionError

    Raised when an extension is requested to be loaded, but it cannot be found.
    """
    def __init__(self, name: str) -> None:
        msg = f'Extension {name!r} could not be loaded.'
        super().__init__(msg, name=name)


class ExtensionAlreadyLoaded(ExtensionError):
    """
    .. inherits_from:: ExtensionError

    Raised when an extension that is being loaded has already been loaded.
    """
    def __init__(self, name: str) -> None:
        msg = f'Extension {name!r} already loaded.'
        super().__init__(msg, name=name)


class ExtensionNotLoaded(ExtensionError):
    """
    .. inherits_from:: ExtensionError

    Raised when an extension that is being unloaded is not currently loaded.
    """
    def __init__(self, name: str) -> None:
        msg = f'Extension {name!r} has not been loaded.'
        super().__init__(msg, name=name)


class ExtensionEntryPointError(ExtensionError):
    """
    .. inherits_from:: ExtensionError

    Raised when an extension is being loaded, but not ``setup`` entry point function was found.
    """
    def __init__(self, name: str) -> None:
        msg = f'Extension {name!r} has no "setup" function.'
        super().__init__(msg, name=name)


class ExtensionFailed(ExtensionError):
    """
    .. inherits_from:: ExtensionError

    Raised when an extension fails to load during the module ``setup`` entry point function.

    Attributes
    ----------
        original: :exc:`Exception`
            The original exception that was raised. This can also be found in the ``__cause__`` attribute.
    """
    original: Exception

    def __init__(self, name: str, original: Exception) -> None:
        self.original: Exception = original
        msg = f'Extension {name!r} raised an error: {original.__class__.__name__}: {original}'
        super().__init__(msg, name=name)


# ======================
#    Client Errors
# ======================
class ClientError(FrameworkException):
    """
    .. inherits_from:: FrameworkException

    The parent exception for any client-specific errors.
    """
    pass


class AsyncClientError(ClientError):
    """
    .. inherits_from:: ClientError

    The parent exception for any async client-specific errors.
    """
    pass


class SyncClientError(ClientError):
    """
    .. inherits_from:: ClientError

    The parent exception for any sync client-specific errors.
    """
    pass


class SubClientError(ClientError):
    """
    .. inherits_from:: ClientError

    The base exception for errors related to :class:`SubClients <arya_api_framework.SubClient>`.

    Attributes
    ----------
        name: :py:class:`str`
            The :class:`SubClient <arya_api_framework.SubClient>` that had an error.
    """
    name: str

    def __init__(self, message: Optional[str] = None, *args: Any, name: str) -> None:
        self.name = name
        message = message or f'SubClient {name!r} has en error.'
        super().__init__(message, *args)


class SubClientAlreadyLoaded(SubClientError):
    """
    .. inherits_from:: SubClientError

    Raised when a :class:`SubClient <arya_api_framework.SubClient>` that is being loaded has already been loaded.
    """
    def __init__(self, name: str) -> None:
        msg = f'SubClient {name!r} already loaded.'
        super().__init__(msg, name=name)


class SubClientParentSet(SubClientAlreadyLoaded):
    """
    .. inherits_from:: SubClientAlreadyLoaded

    Raised when a :class:`SubClient <arya_api_framework.SubClient>` that is being loaded already has a
    :attr:`parent <arya_api_framework.SubClient.parent>` set, meaning it has been previously loaded.
    """
    def __init__(self, name: str) -> None:
        super().__init__(name=name)


class SubClientNotLoaded(SubClientError):
    """
    .. inherits_from:: SubClientError

    Raised when a :class:`SubClient <arya_api_framework.SubClient>` that is being unloaded is not currently loaded.
    """
    def __init__(self, name: str) -> None:
        msg = f'SubClient {name!r} has not been loaded.'
        super().__init__(msg, name=name)


class SubClientNoParent(SubClientError):
    """
    .. inherits_from:: SubClientError

    Raised when a :class:`SubClient <arya_api_framework.SubClient>` method that requires a
    :attr:`parent <arya_api_framework.SubClient.parent>` is called, but no parent is found.
    """
    def __init__(self, name: str) -> None:
        msg = f'SubClient {name!r} has no parent that can execute this action.'
        super().__init__(msg, name=name)


# ======================
#    Request Errors
# ======================
class ResponseParseError(ClientError):
    """
    .. inherits_from:: ClientError

    The exception for failure to parse the response to request.

    This is usually raised if the response body was not readable by :py:func:`json.loads`.

    Attributes
    ----------
        raw_response: Union[:py:class:`str`, :py:class:`bytes`]
            The raw response that was unable to be parsed.
    """
    raw_response: RawResponse

    def __init__(self, raw_response: RawResponse):
        self.raw_response = raw_response


class HTTPError(FrameworkException):
    """
    .. inherits_from:: FrameworkException

    The base exception for any request errors.

    See :ref:`http-status-codes` for information about HTTP status codes.

    Attributes
    ----------
        status_code: :py:class:`int`
            The status code of the error.
        response: Union[:py:class:`str`, :py:class:`bytes`, :py:class:`dict`, :py:class:`list`, :class:`BaseModel`]
            The response that was received that raised the error.
    """
    status_code: int = None
    response: Response = None

    def __init__(self, response: Response, msg: Optional[str] = None):
        self.response = response

        if msg is not None:
            super().__init__(msg)


class HTTPRedirect(HTTPError):
    """
    .. inherits_from:: HTTPError

    Raised for any ``3xx Redirection`` responses.

    These codes indicate that further action needs to be taken by the user in order to fulfill the request.

    See :ref:`3xx` for information about ``3xx`` responses.
    """
    pass


class HTTPClientError(HTTPError):
    """
    .. inherits_from:: HTTPError

    Raised for any ``4xx Client Error`` responses.

    These codes occur when an error has occurred as a result of the client application or user input,
    such as a malformed request.

    See :ref:`4xx` for information about ``4xx`` responses.
    """
    pass


class HTTPServerError(HTTPError):
    """
    .. inherits_from:: HTTPError

    Raised for any ``5xx Server Error`` responses.

    These codes occur when the server is aware that is has made an error, or is incapable of performing the request.

    See :ref:`5xx` for information about ``5xx`` responses.
    """
    pass


# 300
class HTTPMultipleChoices(HTTPRedirect):
    """
    .. inherits_from:: HTTPRedirect

    :ref:`300`
    """
    status_code = HTTPStatus.HTTP_300_MULTIPLE_CHOICES


class HTTPMovedPermanently(HTTPRedirect):
    """
    .. inherits_from:: HTTPRedirect

    :ref:`301`
    """
    status_code = HTTPStatus.HTTP_301_MOVED_PERMANENTLY


class HTTPFound(HTTPRedirect):
    """
    .. inherits_from:: HTTPRedirect

    :ref:`302`
    """
    status_code = HTTPStatus.HTTP_302_FOUND


class HTTPSeeOther(HTTPRedirect):
    """
    .. inherits_from:: HTTPRedirect

    :ref:`303`
    """
    status_code = HTTPStatus.HTTP_303_SEE_OTHER


class HTTPNotModified(HTTPRedirect):
    """
    .. inherits_from:: HTTPRedirect

    :ref:`304`
    """
    status_code = HTTPStatus.HTTP_304_NOT_MODIFIED


class HTTPUseProxy(HTTPRedirect):
    """
    .. inherits_from:: HTTPRedirect

    :ref:`305`
    """
    status_code = HTTPStatus.HTTP_305_USE_PROXY


class HTTPReserved(HTTPRedirect):
    """
    .. inherits_from:: HTTPRedirect

    :ref:`306`
    """
    status_code = HTTPStatus.HTTP_306_RESERVED


class HTTPTemporaryRedirect(HTTPRedirect):
    """
    .. inherits_from:: HTTPRedirect

    :ref:`307`
    """
    status_code = HTTPStatus.HTTP_307_TEMPORARY_REDIRECT


class HTTPPermanentRedirect(HTTPRedirect):
    """
    .. inherits_from:: HTTPRedirect

    :ref:`308`
    """

    status_code = HTTPStatus.HTTP_308_PERMANENT_REDIRECT


# 400
class HTTPBadRequest(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`400`
    """
    status_code = HTTPStatus.HTTP_400_BAD_REQUEST


class HTTPUnauthorized(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`401`
    """
    status_code = HTTPStatus.HTTP_401_UNAUTHORIZED


class HTTPPaymentRequired(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`402`
    """
    status_code = HTTPStatus.HTTP_402_PAYMENT_REQUIRED


class HTTPForbidden(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`403`
    """

    status_code = HTTPStatus.HTTP_403_FORBIDDEN


class HTTPNotFound(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`404`
    """
    status_code = HTTPStatus.HTTP_404_NOT_FOUND

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(None, msg='That page could not be found.')


class HTTPMethodNotAllowed(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`405`
    """
    status_code = HTTPStatus.HTTP_405_METHOD_NOT_ALLOWED


class HTTPNotAcceptable(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`406`
    """
    status_code = HTTPStatus.HTTP_406_NOT_ACCEPTABLE


class HTTPProxyAuthenticationRequired(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`407`
    """
    status_code = HTTPStatus.HTTP_407_PROXY_AUTHENTICATION_REQUIRED


class HTTPRequestTimeout(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`408`
    """
    status_code = HTTPStatus.HTTP_408_REQUEST_TIMEOUT


class HTTPConflict(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`409`
    """
    status_code = HTTPStatus.HTTP_409_CONFLICT


class HTTPGone(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`410`
    """
    status_code = HTTPStatus.HTTP_410_GONE


class HTTPLengthRequired(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`411`
    """
    status_code = HTTPStatus.HTTP_411_LENGTH_REQUIRED


class HTTPPreconditionFailed(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`412`
    """
    status_code = HTTPStatus.HTTP_412_PRECONDITION_FAILED


class HTTPRequestEntityTooLarge(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`413`
    """
    status_code = HTTPStatus.HTTP_413_REQUEST_ENTITY_TOO_LARGE


class HTTPRequestUriTooLong(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`414`
    """
    status_code = HTTPStatus.HTTP_414_REQUEST_URI_TOO_LONG


class HTTPUnsupportedMediaType(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`415`
    """
    status_code = HTTPStatus.HTTP_415_UNSUPPORTED_MEDIA_TYPE


class HTTPRequestedRangeNotSatisfiable(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`416`
    """
    status_code = HTTPStatus.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE


class HTTPExpectationFailed(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`417`
    """
    status_code = HTTPStatus.HTTP_417_EXPECTATION_FAILED


class HTTPImATeapot(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`418`
    """
    status_code = HTTPStatus.HTTP_418_IM_A_TEAPOT


class HTTPMisdirectedRequest(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`421`
    """
    status_code = HTTPStatus.HTTP_421_MISDIRECTED_REQUEST


class HTTPUnprocessableEntity(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`422`
    """
    status_code = HTTPStatus.HTTP_422_UNPROCESSABLE_ENTITY


class HTTPFailedDependency(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`424`
    """
    status_code = HTTPStatus.HTTP_424_FAILED_DEPENDENCY


class HTTPTooEarly(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`425`
    """
    status_code = HTTPStatus.HTTP_425_TOO_EARLY


class HTTPUpgradeRequired(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`426`
    """
    status_code = HTTPStatus.HTTP_426_UPGRADE_REQUIRED


class HTTPPreconditionRequired(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`428`
    """
    status_code = HTTPStatus.HTTP_428_PRECONDITION_REQUIRED


class HTTPTooManyRequests(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`429`
    """
    status_code = HTTPStatus.HTTP_429_TOO_MANY_REQUESTS


class HTTPRequestHeaderFieldsTooLarge(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`431`
    """
    status_code = HTTPStatus.HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE


class HTTPUnavailableForLegalReasons(HTTPClientError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`451`
    """
    status_code = HTTPStatus.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS


# 500
class HTTPInternalServerError(HTTPServerError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`500`
    """
    status_code = HTTPStatus.HTTP_500_INTERNAL_SERVER_ERROR


class HTTPNotImplemented(HTTPServerError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`501`
    """
    status_code = HTTPStatus.HTTP_501_NOT_IMPLEMENTED


class HTTPBadGateway(HTTPServerError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`502`
    """
    status_code = HTTPStatus.HTTP_502_BAD_GATEWAY


class HTTPServiceUnavailable(HTTPServerError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`503`
    """
    status_code = HTTPStatus.HTTP_503_SERVICE_UNAVAILABLE


class HTTPGatewayTimeout(HTTPServerError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`504`
    """
    status_code = HTTPStatus.HTTP_504_GATEWAY_TIMEOUT


class HTTPHttpServerVersionNotSupported(HTTPServerError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`505`
    """
    status_code = HTTPStatus.HTTP_505_HTTP_VERSION_NOT_SUPPORTED


class HTTPVariantAlsoNegotiates(HTTPServerError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`506`
    """
    status_code = HTTPStatus.HTTP_506_VARIANT_ALSO_NEGOTIATES


class HTTPInsufficientStorage(HTTPServerError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`507`
    """
    status_code = HTTPStatus.HTTP_507_INSUFFICIENT_STORAGE


class HTTPLoopDetected(HTTPServerError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`508`
    """
    status_code = HTTPStatus.HTTP_508_LOOP_DETECTED


class HTTPNotExtended(HTTPServerError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`510`
    """
    status_code = HTTPStatus.HTTP_510_NOT_EXTENDED


class HTTPNetworkAuthenticationRequired(HTTPServerError):
    """
    .. inherits_from:: HTTPClientError

    :ref:`511`
    """
    status_code = HTTPStatus.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED


# Map errors codes to their related exception classes.
ERROR_RESPONSE_MAPPING = {
    # 300
    HTTPStatus.HTTP_300_MULTIPLE_CHOICES: HTTPMultipleChoices,
    HTTPStatus.HTTP_301_MOVED_PERMANENTLY: HTTPMovedPermanently,
    HTTPStatus.HTTP_302_FOUND: HTTPFound,
    HTTPStatus.HTTP_303_SEE_OTHER: HTTPSeeOther,
    HTTPStatus.HTTP_304_NOT_MODIFIED: HTTPNotModified,
    HTTPStatus.HTTP_305_USE_PROXY: HTTPUseProxy,
    HTTPStatus.HTTP_306_RESERVED: HTTPReserved,
    HTTPStatus.HTTP_307_TEMPORARY_REDIRECT: HTTPTemporaryRedirect,
    HTTPStatus.HTTP_308_PERMANENT_REDIRECT: HTTPPermanentRedirect,
    # 400
    HTTPStatus.HTTP_400_BAD_REQUEST: HTTPBadRequest,
    HTTPStatus.HTTP_401_UNAUTHORIZED: HTTPUnauthorized,
    HTTPStatus.HTTP_402_PAYMENT_REQUIRED: HTTPPaymentRequired,
    HTTPStatus.HTTP_403_FORBIDDEN: HTTPForbidden,
    HTTPStatus.HTTP_404_NOT_FOUND: HTTPNotFound,
    HTTPStatus.HTTP_405_METHOD_NOT_ALLOWED: HTTPMethodNotAllowed,
    HTTPStatus.HTTP_406_NOT_ACCEPTABLE: HTTPNotAcceptable,
    HTTPStatus.HTTP_407_PROXY_AUTHENTICATION_REQUIRED: HTTPProxyAuthenticationRequired,
    HTTPStatus.HTTP_408_REQUEST_TIMEOUT: HTTPRequestTimeout,
    HTTPStatus.HTTP_409_CONFLICT: HTTPConflict,
    HTTPStatus.HTTP_410_GONE: HTTPGone,
    HTTPStatus.HTTP_411_LENGTH_REQUIRED: HTTPLengthRequired,
    HTTPStatus.HTTP_412_PRECONDITION_FAILED: HTTPPreconditionFailed,
    HTTPStatus.HTTP_413_REQUEST_ENTITY_TOO_LARGE: HTTPRequestEntityTooLarge,
    HTTPStatus.HTTP_414_REQUEST_URI_TOO_LONG: HTTPRequestUriTooLong,
    HTTPStatus.HTTP_415_UNSUPPORTED_MEDIA_TYPE: HTTPUnsupportedMediaType,
    HTTPStatus.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE: HTTPRequestedRangeNotSatisfiable,
    HTTPStatus.HTTP_417_EXPECTATION_FAILED: HTTPExpectationFailed,
    HTTPStatus.HTTP_418_IM_A_TEAPOT: HTTPImATeapot,
    HTTPStatus.HTTP_421_MISDIRECTED_REQUEST: HTTPMisdirectedRequest,
    HTTPStatus.HTTP_422_UNPROCESSABLE_ENTITY: HTTPUnprocessableEntity,
    HTTPStatus.HTTP_424_FAILED_DEPENDENCY: HTTPFailedDependency,
    HTTPStatus.HTTP_425_TOO_EARLY: HTTPTooEarly,
    HTTPStatus.HTTP_426_UPGRADE_REQUIRED: HTTPUpgradeRequired,
    HTTPStatus.HTTP_428_PRECONDITION_REQUIRED: HTTPPreconditionRequired,
    HTTPStatus.HTTP_429_TOO_MANY_REQUESTS: HTTPTooManyRequests,
    HTTPStatus.HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE: HTTPRequestHeaderFieldsTooLarge,
    HTTPStatus.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS: HTTPUnavailableForLegalReasons,
    # 500
    HTTPStatus.HTTP_500_INTERNAL_SERVER_ERROR: HTTPInternalServerError,
    HTTPStatus.HTTP_501_NOT_IMPLEMENTED: HTTPNotImplemented,
    HTTPStatus.HTTP_502_BAD_GATEWAY: HTTPBadGateway,
    HTTPStatus.HTTP_503_SERVICE_UNAVAILABLE: HTTPServiceUnavailable,
    HTTPStatus.HTTP_504_GATEWAY_TIMEOUT: HTTPGatewayTimeout,
    HTTPStatus.HTTP_505_HTTP_VERSION_NOT_SUPPORTED: HTTPHttpServerVersionNotSupported,
    HTTPStatus.HTTP_506_VARIANT_ALSO_NEGOTIATES: HTTPVariantAlsoNegotiates,
    HTTPStatus.HTTP_507_INSUFFICIENT_STORAGE: HTTPInsufficientStorage,
    HTTPStatus.HTTP_508_LOOP_DETECTED: HTTPLoopDetected,
    HTTPStatus.HTTP_510_NOT_EXTENDED: HTTPNotExtended,
    HTTPStatus.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED: HTTPNetworkAuthenticationRequired,
}
