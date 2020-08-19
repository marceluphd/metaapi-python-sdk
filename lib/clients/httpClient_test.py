from .httpClient import HttpClient
import re
import pytest
import responses
httpClient = None
test_url = 'http://example.com'


@pytest.fixture(autouse=True)
async def run_around_tests():
    global httpClient
    httpClient = HttpClient()
    yield


class TestHttpClient:
    @pytest.mark.asyncio
    async def test_load(self):
        """Should load HTML page from example.com"""
        opts = {
            'url': test_url
        }
        response = await httpClient.request(opts)
        text = response.text
        assert re.search('doctype html', text)

    @pytest.mark.asyncio
    async def test_not_found(self):
        """Should return NotFound exception if server returns 404"""
        opts = {
            'url': f'{test_url}/not-found'
        }
        try:
            await httpClient.request(opts)
            raise Exception('NotFoundException is expected')
        except Exception as err:
            assert err.__class__.__name__ == 'NotFoundException'

    @pytest.mark.asyncio
    async def test_timeout(self):
        """Should return ConnectTimeout exception if request is timed out"""
        httpClient = HttpClient(0.001)
        opts = {
            'url': test_url
        }
        try:
            await httpClient.request(opts)
            raise Exception('ConnectTimeout is expected')
        except Exception as err:
            assert err.__class__.__name__ == 'ConnectTimeout'

    @pytest.mark.asyncio
    async def test_validation_exception(self):
        """Should return a validation exception"""
        with responses.RequestsMock() as rsps:
            error = {
                'id': 1,
                'error': 'error',
                'message': 'test message',
            }
            rsps.add(responses.POST, test_url, json=error, status=400)
            opts = {
                'method': 'POST',
                'url': test_url
            }
            try:
                await httpClient.request(opts)
                raise Exception('ValidationException is expected')
            except Exception as err:
                assert err.__class__.__name__ == 'ValidationException'
                assert err.__str__() == 'test message'

    @pytest.mark.asyncio
    async def test_validation_exception_details(self):
        """Should return a validation exception with details"""
        with responses.RequestsMock() as rsps:
            error = {
                'id': 1,
                'error': 'error',
                'message': 'test',
                'details': [{'parameter': 'password', 'value': 'wrong', 'message': 'Invalid value'}]
            }
            rsps.add(responses.POST, test_url, json=error, status=400)
            opts = {
                'method': 'POST',
                'url': test_url
            }
            try:
                await httpClient.request(opts)
                raise Exception('ValidationException is expected')
            except Exception as err:
                assert err.__class__.__name__ == 'ValidationException'
                assert err.__str__() == 'test'
                assert err._details == error['details']
