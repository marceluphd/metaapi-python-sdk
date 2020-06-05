from lib.clients.errorHandler import UnauthorizedException, ForbiddenException, ApiException, ConflictException, \
    ValidationException, InternalException, NotFoundException
import requests


class HttpClient:
    """HTTP client library based on requests module."""

    async def request(self, options):
        """Performs a request. Response errors are returned as ApiError or subclasses.

        :param options: request options
        :returns: promise returning request results"""
        response = await self._make_request(options)
        try:
            response.raise_for_status()
        except Exception as err:
            response = self._convert_error(err)
        return response

    async def _make_request(self, options):
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

    def _convert_error(self, err):
        status = err.response.status_code
        if status == 400:
            return ValidationException(err.response.reason, err.details)
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
