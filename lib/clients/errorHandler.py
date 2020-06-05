class ApiException(Exception):
    """Base class for API exceptions. Contains indication of HTTP status.

    Attributes:
        status_code: HTTP status code
    """

    def __init__(self, message, status):
        """Inits ApiException

        :param message: exception message
        :type message: str
        :param status: HTTP status
        :type status: int
        """
        super().__init__(message)
        self.status_code = status

    @property
    def code(self):
        """Returns exception code used for i18n

        :returns: exception code
        """
        return self._code

    @code.setter
    def code(self, code):
        """Sets error code, used for i18n

        :param code: error code for i18n
        """
        self._code = code

    @property
    def arguments(self):
        """Returns message arguments for i18n

        :returns: message arguments for i18n
        """
        return self.args

    @arguments.setter
    def arguments(self, args):
        """Set message arguments for i18n

        :param args: arguments for i18n
        :type args: list
        """
        self.args = args


class NotFoundException(ApiException):
    """Throwing this exception results in 404 (Not Found) HTTP response code."""

    def __init__(self, message):
        """Inits not found exception.

        :param message: exception message
        :type message: str
        """
        super().__init__(message, 404)


class ForbiddenException(ApiException):
    """Throwing this exception results in 403 (Forbidden) HTTP response code."""

    def __init__(self, message):
        """Inits forbidden exception.

        :param message: exception message
        :type message: str
        """
        super().__init__(message, 403)


class UnauthorizedException(ApiException):
    """Throwing this exception results in 401 (Unauthorized) HTTP response code."""

    def __init__(self, message):
        """Inits unauthorized exception.

        :param message: exception message
        :type message: str
        """
        super().__init__(message, 401)


class ValidationException(ApiException):
    """Represents validation exception. Throwing this exception results in 400 (Bad Request) HTTP response code.

    Attributes:
        _details: Validation exception details
    """

    def __init__(self, message, details):
        """Inits validation error.

        :param message: exception message
        :type message: str
        :param details: exception data
        :type details: dict
        """
        super().__init__(message, 400)
        self._details = details


class InternalException(ApiException):
    """Represents unexpected exception. Throwing this error results in 500 (Internal Error) HTTP response code."""

    def __init__(self, message):
        """Inits unexpected exception.

        :param message: exception message
        :type message: str
        """
        super().__init__(message, 500)


class ConflictException(ApiException):
    """Represents conflict exception. Throwing this exception results in 409 (Conflict) HTTP response code."""

    def __init__(self, message):
        """Inits conflict exception.

        :param message: exception message
        :type message: str
        """
        super().__init__(message, 409)
