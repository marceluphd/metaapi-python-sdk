import responses
import pytest
from ..httpClient import HttpClient
from .metatraderDemoAccount_client import MetatraderDemoAccountClient
PROVISIONING_API_URL = 'https://mt-provisioning-api-v1.agiliumtrade.agiliumtrade.ai'
http_client = HttpClient()
demo_account_client = MetatraderDemoAccountClient(http_client, 'header.payload.sign')


class TestMetatraderDemoAccountClient:
    @responses.activate
    @pytest.mark.asyncio
    async def test_create_mt4(self):
        """Should create new MetaTrader 4 demo from API."""
        expected = {
            'login': '12345',
            'password': 'qwerty',
            'serverName': 'HugosWay-Demo3',
            'investorPassword': 'qwerty'
        }
        account = {
            'balance': 10,
            'email': 'test@test.com',
            'leverage': 15,
            'serverName': 'server'
        }
        with responses.RequestsMock() as rsps:
            rsps.add(responses.POST, f'{PROVISIONING_API_URL}/users/current/provisioning-profiles/'
                                     'profileId1/mt4-demo-accounts',
                     json=expected, status=200)

            accounts = await demo_account_client.create_mt4_demo_account('profileId1', account)
            assert rsps.calls[0].request.url == f'{PROVISIONING_API_URL}/users/current/provisioning-profiles/' + \
                'profileId1/mt4-demo-accounts'
            assert rsps.calls[0].request.method == 'POST'
            assert rsps.calls[0].request.headers['auth-token'] == 'header.payload.sign'
            assert accounts == expected

    @pytest.mark.asyncio
    async def test_not_create_mt4_demo_with_account_token(self):
        """Should not create MetaTrader 4 demo account via API with account token'."""
        account_client = MetatraderDemoAccountClient(http_client, 'token')
        try:
            await account_client.create_mt4_demo_account('', {})
        except Exception as err:
            assert err.__str__() == 'You can not invoke create_mt4_demo_account method, because you have ' + \
                                    'connected with account access token. Please use API access token from ' + \
                                    'https://app.metaapi.cloud/token page to invoke this method.'

    @responses.activate
    @pytest.mark.asyncio
    async def test_create_mt5(self):
        """Should create new MetaTrader 4 demo from API."""
        expected = {
            'login': '12345',
            'password': 'qwerty',
            'serverName': 'HugosWay-Demo3',
            'investorPassword': 'qwerty'
        }
        account = {
            'balance': 10,
            'email': 'test@test.com',
            'leverage': 15,
            'serverName': 'server'
        }
        with responses.RequestsMock() as rsps:
            rsps.add(responses.POST, f'{PROVISIONING_API_URL}/users/current/provisioning-profiles/'
                                     'profileId2/mt5-demo-accounts',
                     json=expected, status=200)

            accounts = await demo_account_client.create_mt5_demo_account('profileId2', account)
            assert rsps.calls[0].request.url == f'{PROVISIONING_API_URL}/users/current/provisioning-profiles/' + \
                   'profileId2/mt5-demo-accounts'
            assert rsps.calls[0].request.method == 'POST'
            assert rsps.calls[0].request.headers['auth-token'] == 'header.payload.sign'
            assert accounts == expected

    @pytest.mark.asyncio
    async def test_not_create_mt5_demo_with_account_token(self):
        """Should not create MetaTrader 5 demo account via API with account token'."""
        account_client = MetatraderDemoAccountClient(http_client, 'token')
        try:
            await account_client.create_mt5_demo_account('', {})
        except Exception as err:
            assert err.__str__() == 'You can not invoke create_mt5_demo_account method, because you have ' + \
                                    'connected with account access token. Please use API access token from ' + \
                                    'https://app.metaapi.cloud/token page to invoke this method.'
