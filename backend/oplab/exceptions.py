"""
Custom exception classes for OPLAB API client.
"""


class OPLABException(Exception):
    """Base exception for all OPLAB API errors."""
    pass


class OPLABUnauthorizedError(OPLABException):
    """Raised when authentication fails (401)."""
    pass


class OPLABPaymentRequiredError(OPLABException):
    """Raised when subscription has expired (402)."""
    pass


class OPLABForbiddenError(OPLABException):
    """Raised when plan doesn't allow access to resource (403)."""
    pass


class OPLABNotFoundError(OPLABException):
    """Raised when resource is not found (404)."""
    pass


class OPLABPreconditionFailedError(OPLABException):
    """Raised when action requirements are not met (412)."""
    pass


class OPLABUnprocessableEntityError(OPLABException):
    """Raised when request cannot be processed (422)."""
    pass


class OPLABRateLimitError(OPLABException):
    """Raised when rate limit is exceeded (429)."""
    pass


class OPLABServerError(OPLABException):
    """Raised when server error occurs (500, 503)."""
    pass

