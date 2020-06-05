import lib.clients.httpClient as httpClient
import re
import pytest
httpClient = httpClient.HttpClient()


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
        response = await httpClient.request(opts)
        assert response.__class__.__name__ == 'NotFoundException'
