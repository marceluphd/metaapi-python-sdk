from ..httpClient import HttpClient
from .trading_client import TradingClient
import pytest
import responses
copy_factory_api_url = 'https://trading-api-v1.agiliumtrade.agiliumtrade.ai'
http_client = HttpClient()
trading_client = TradingClient(http_client, 'header.payload.sign')


@pytest.fixture(autouse=True)
async def run_around_tests():
    global http_client
    global trading_client
    http_client = HttpClient()
    trading_client = TradingClient(http_client, 'header.payload.sign')


class TestTradingClient:
    @pytest.mark.asyncio
    async def test_resynchronize_copyfactory_account(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.POST, f'{copy_factory_api_url}/users/current/accounts/' +
                     '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef/resynchronize?strategyId=ABCD',
                     status=200)
            await trading_client.resynchronize('0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
                                               ['ABCD'])
            assert rsps.calls[0].request.method == 'POST'
            assert rsps.calls[0].request.headers['auth-token'] == 'header.payload.sign'

    @pytest.mark.asyncio
    async def test_not_resynchronize_account_with_account_token(self):
        """Should not resynchronize account with account token."""
        trading_client = TradingClient(http_client, 'token')
        try:
            await trading_client.resynchronize('0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
                                               ['ABCD'])
        except Exception as err:
            assert err.__str__() == 'You can not invoke resynchronize method, ' + \
                   'because you have connected with account access token. Please use API access token from ' + \
                   'https://app.metaapi.cloud/token page to invoke this method.'

    @pytest.mark.asyncio
    async def test_retrieve_stopouts(self):
        """Should retrieve stopouts."""
        expected = [{
          'reason': 'max-drawdown',
          'stoppedAt': '2020-08-08T07:57:30.328Z',
          'strategy': {
            'id': 'ABCD',
            'name': 'Strategy'
          },
          'reasonDescription': 'total strategy equity drawdown exceeded limit'
        }]
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{copy_factory_api_url}/users/current/accounts/' +
                     '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef/stopouts',
                     json=expected, status=200)
            stopouts = await trading_client.get_stopouts('0123456789abcdef0123456789abcdef0123456789abcdef' +
                                                         '0123456789abcdef')
            assert rsps.calls[0].request.url == f'{copy_factory_api_url}/users/current/accounts/' + \
                '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef/stopouts'
            assert rsps.calls[0].request.method == 'GET'
            assert rsps.calls[0].request.headers['auth-token'] == 'header.payload.sign'
            assert stopouts == expected

    @pytest.mark.asyncio
    async def test_not_retrieve_stopouts_with_account_token(self):
        """Should not retrieve stopouts from API with account token."""
        trading_client = TradingClient(http_client, 'token')
        try:
            await trading_client.get_stopouts('0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef')
        except Exception as err:
            assert err.__str__() == 'You can not invoke get_stopouts method, ' + \
                   'because you have connected with account access token. Please use API access token from ' + \
                   'https://app.metaapi.cloud/token page to invoke this method.'

    @pytest.mark.asyncio
    async def test_reset_stopout(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.POST, f'{copy_factory_api_url}/users/current/accounts/' +
                     '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef/stopouts/daily-equity/reset',
                     status=200)
            await trading_client.reset_stopout('0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
                                               'daily-equity')
            assert rsps.calls[0].request.method == 'POST'
            assert rsps.calls[0].request.headers['auth-token'] == 'header.payload.sign'

    @pytest.mark.asyncio
    async def test_not_reset_stopout_with_account_token(self):
        """Should not reset stopout with account token."""
        trading_client = TradingClient(http_client, 'token')
        try:
            await trading_client.reset_stopout('0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
                                               'daily-equity')
        except Exception as err:
            assert err.__str__() == 'You can not invoke reset_stopout method, ' + \
                   'because you have connected with account access token. Please use API access token from ' + \
                   'https://app.metaapi.cloud/token page to invoke this method.'
