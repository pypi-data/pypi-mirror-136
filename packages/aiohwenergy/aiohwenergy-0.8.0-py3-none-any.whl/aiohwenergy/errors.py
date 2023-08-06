"""Aiohwenergy errors."""


class AiohwenergyException(Exception):
    """Base error for aiohwenergy."""


class RequestError(AiohwenergyException):
    """Unable to fulfill request.

    Raised when host or API cannot be reached.
    """


class InvalidStateError(AiohwenergyException):
    """Raised when the device is not in the correct state."""


class UnsupportedError(AiohwenergyException):
    """Raised when the device is not supported from this library."""


class DisabledError(AiohwenergyException):
    """Raised when device API is disabled. User has to enable API in app."""
