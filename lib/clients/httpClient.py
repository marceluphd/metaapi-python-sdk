from .errorHandler import UnauthorizedException, ForbiddenException, ApiException, ConflictException, \
    ValidationException, InternalException, NotFoundException
import requests
from typing_extensions import TypedDict
from typing import Optional


class RequestOptions(TypedDict):
    """Options for HttpClient requests."""
    method: Optional[str]
    url: str
    headers: Optional[dict]
    params: Optional[dict]
    body: Optional[dict]
    files: Optional[dict]


class HttpClient:
    """HTTP client library based on requests module."""
    def __init__(self, timeout: float = 60):
        self._timeout = timeout

    async def request(self, options: RequestOptions) -> requests.Response:
        """Performs a request. Response errors are returned as ApiError or subclasses.

        Args:
            options: Request options.

        Returns:
            A request response.
        """
        response = await self._make_request(options)
        try:
            response.raise_for_status()
            if response.content:
                try:
                    response = response.json()
                except Exception as err:
                    print('Error parsing json', err)
        except requests.HTTPError as err:
            self._convert_error(err)
        return response

    async def _make_request(self, options: RequestOptions) -> requests.Response:
        req = requests.Request()
        req.method = options['method'] if ('method' in options) else 'GET'
        req.url = options['url']
        if 'params' in options:
            req.params = options['params']
        if 'files' in options:
            req.files = options['files']
        if 'headers' in options:
            req.headers = options['headers']
        if 'body' in options:
            req.json = options['body']
        prepped = req.prepare()
        s = requests.Session()
        return s.send(prepped, timeout=self._timeout)

    def _convert_error(self, err: requests.HTTPError):
        status = err.response.status_code
        if status == 400:
            validation_text = err.response.text['message'] if isinstance(err.response.text, dict) else err.response.text
            raise ValidationException(err.response.reason, validation_text)
        elif status == 401:
            raise UnauthorizedException(err.response.reason)
        elif status == 403:
            raise ForbiddenException(err.response.reason)
        elif status == 404:
            raise NotFoundException(err.response.reason)
        elif status == 409:
            raise ConflictException(err.response.reason)
        elif status == 500:
            raise InternalException(err.response.reason)
        else:
            raise ApiException(err.response.reason, status)
