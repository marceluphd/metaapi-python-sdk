from .httpClient import HttpClient
import re
import pytest
httpClient = None


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
            'url': 'http://example.com'
        }
        response = await httpClient.request(opts)
        text = response.text
        assert re.search('doctype html', text)

    @pytest.mark.asyncio
    async def test_not_found(self):
        """Should return NotFound exception if server returns 404"""
        opts = {
            'url': 'http://example.com/not-found'
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
            'url': 'http://example.com/'
        }
        try:
            await httpClient.request(opts)
            raise Exception('ConnectTimeout is expected')
        except Exception as err:
            assert err.__class__.__name__ == 'ConnectTimeout'
