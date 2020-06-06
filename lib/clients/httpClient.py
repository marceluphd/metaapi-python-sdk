from lib.clients.errorHandler import UnauthorizedException, ForbiddenException, ApiException, ConflictException, \
    ValidationException, InternalException, NotFoundException
import requests
import json
from typing import TypedDict, Optional


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
        except requests.HTTPError as err:
            response = self._convert_error(err)
        return response

    async def _make_request(self, options) -> requests.Response:
        if 'method' not in options:
            options['method'] = 'GET'
        if 'headers' not in options:
            options['headers'] = {}
        if 'params' not in options:
            options['params'] = {}
        if 'files' not in options:
            options['files'] = {}
        s = requests.Session()
        req = requests.Request(options['method'], options['url'], params=options['params'], files=options['files'])
        prepped = req.prepare()
        if 'body' in options:
            prepped.body = options['body']
        prepped.headers = options['headers']
        return s.send(prepped)

    def _convert_error(self, err: requests.HTTPError) -> ApiException:
        status = err.response.status_code
        if status == 400:
            return ValidationException(err.response.reason, json.loads(err.response.text)['details'])
        elif status == 401:
            return UnauthorizedException(err.response.reason)
        elif status == 403:
            return ForbiddenException(err.response.reason)
        elif status == 404:
            return NotFoundException(err.response.reason)
        elif status == 409:
            return ConflictException(err.response.reason)
        elif status == 500:
            return InternalException(err.response.reason)
        else:
            return ApiException(err.response.reason, status)
