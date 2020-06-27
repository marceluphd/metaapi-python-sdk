import responses
import pytest
from .httpClient import HttpClient
from .metatraderAccount_client import MetatraderAccountClient
import json

PROVISIONING_API_URL = 'https://mt-provisioning-api-v1.agiliumtrade.agiliumtrade.ai'
httpClient = HttpClient()
provisioningClient = MetatraderAccountClient(httpClient, 'token')


class TestMetatraderAccountClient:
    @responses.activate
    @pytest.mark.asyncio
    async def test_retrieve_many(self):
        """Should retrieve MetaTrader accounts from API."""
        expected = [{
            '_id': '1eda642a-a9a3-457c-99af-3bc5e8d5c4c9',
            'login': '50194988',
            'name': 'mt5a',
            'server': 'ICMarketsSC-Demo',
            'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
            'magic': 123456,
            'timeConverter': 'icmarkets',
            'application': 'MetaApi',
            'connectionStatus': 'DISCONNECTED',
            'state': 'DEPLOYED',
            'synchronizationMode': 'automatic',
            'type': 'cloud'
        }]

        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{PROVISIONING_API_URL}/users/current/accounts',
                     json=expected, status=200)

            accounts = await provisioningClient.get_accounts('f9ce1f12-e720-4b9a-9477-c2d4cb25f076')
            assert rsps.calls[0].request.url == f'{PROVISIONING_API_URL}/users/current/accounts' + \
                '?provisioningProfileId=f9ce1f12-e720-4b9a-9477-c2d4cb25f076'
            assert rsps.calls[0].request.method == 'GET'
            assert rsps.calls[0].request.headers['auth-token'] == 'token'
            assert accounts == expected

    @responses.activate
    @pytest.mark.asyncio
    async def test_retrieve_one(self):
        """Should retrieve MetaTrader account from API."""
        expected = {
            '_id': 'id',
            'login': '50194988',
            'name': 'mt5a',
            'server': 'ICMarketsSC-Demo',
            'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
            'magic': 123456,
            'timeConverter': 'icmarkets',
            'application': 'MetaApi',
            'connectionStatus': 'DISCONNECTED',
            'state': 'DEPLOYED',
            'synchronizationMode': 'automatic',
            'type': 'cloud'
        }

        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{PROVISIONING_API_URL}/users/current/accounts/id',
                     json=expected, status=200)

            accounts = await provisioningClient.get_account('id')
            assert rsps.calls[0].request.url == f'{PROVISIONING_API_URL}/users/current/accounts/id'
            assert rsps.calls[0].request.method == 'GET'
            assert rsps.calls[0].request.headers['auth-token'] == 'token'
            assert accounts == expected

    @responses.activate
    @pytest.mark.asyncio
    async def test_create(self):
        """Should create MetaTrader account via API."""
        expected = {
            'id': 'id'
        }
        account = {
            'login': '50194988',
            'password': 'Test1234',
            'name': 'mt5a',
            'server': 'ICMarketsSC-Demo',
            'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
            'magic': 123456,
            'timeConverter': 'icmarkets',
            'application': 'MetaApi',
            'synchronizationMode': 'automatic',
            'type': 'cloud'
        }
        with responses.RequestsMock() as rsps:
            rsps.add(responses.POST, f'{PROVISIONING_API_URL}/users/current/accounts',
                     json=expected, status=201)

            accounts = await provisioningClient.create_account(account)
            assert rsps.calls[0].request.url == f'{PROVISIONING_API_URL}/users/current/accounts'
            assert rsps.calls[0].request.method == 'POST'
            assert rsps.calls[0].request.headers['auth-token'] == 'token'
            assert accounts == expected

    @responses.activate
    @pytest.mark.asyncio
    async def test_deploy(self):
        """Should deploy MetaTrader account via API."""
        with responses.RequestsMock() as rsps:
            rsps.add(responses.POST, f'{PROVISIONING_API_URL}/users/current/accounts/id/deploy', status=204)

            await provisioningClient.deploy_account('id')
            assert rsps.calls[0].request.url == f'{PROVISIONING_API_URL}/users/current/accounts/id/deploy'
            assert rsps.calls[0].request.method == 'POST'
            assert rsps.calls[0].request.headers['auth-token'] == 'token'

    @responses.activate
    @pytest.mark.asyncio
    async def test_undeploy(self):
        """Should undeploy MetaTrader account via API."""
        with responses.RequestsMock() as rsps:
            rsps.add(responses.POST, f'{PROVISIONING_API_URL}/users/current/accounts/id/undeploy', status=204)

            await provisioningClient.undeploy_account('id')
            assert rsps.calls[0].request.url == f'{PROVISIONING_API_URL}/users/current/accounts/id/undeploy'
            assert rsps.calls[0].request.method == 'POST'
            assert rsps.calls[0].request.headers['auth-token'] == 'token'

    @responses.activate
    @pytest.mark.asyncio
    async def test_redeploy(self):
        """Should redeploy MetaTrader account via API."""
        with responses.RequestsMock() as rsps:
            rsps.add(responses.POST, f'{PROVISIONING_API_URL}/users/current/accounts/id/redeploy', status=204)

            await provisioningClient.redeploy_account('id')
            assert rsps.calls[0].request.url == f'{PROVISIONING_API_URL}/users/current/accounts/id/redeploy'
            assert rsps.calls[0].request.method == 'POST'
            assert rsps.calls[0].request.headers['auth-token'] == 'token'

    @responses.activate
    @pytest.mark.asyncio
    async def test_delete(self):
        """Should delete MetaTrader account via API."""
        with responses.RequestsMock() as rsps:
            rsps.add(responses.DELETE, f'{PROVISIONING_API_URL}/users/current/accounts/id', status=204)

            await provisioningClient.delete_account('id')
            assert rsps.calls[0].request.url == f'{PROVISIONING_API_URL}/users/current/accounts/id'
            assert rsps.calls[0].request.method == 'DELETE'
            assert rsps.calls[0].request.headers['auth-token'] == 'token'

    @responses.activate
    @pytest.mark.asyncio
    async def test_update(self):
        """Should update MetaTrader account via API."""
        update_account = {
              'name': 'new account name',
              'password': 'new_password007',
              'server': 'ICMarketsSC2-Demo',
              'synchronizationMode': 'user'
            }
        with responses.RequestsMock() as rsps:
            rsps.add(responses.PUT, f'{PROVISIONING_API_URL}/users/current/accounts/id', status=204)

            await provisioningClient.update_account('id', update_account)
            assert rsps.calls[0].request.url == f'{PROVISIONING_API_URL}/users/current/accounts/id'
            assert rsps.calls[0].request.method == 'PUT'
            assert rsps.calls[0].request.headers['auth-token'] == 'token'
            assert rsps.calls[0].request.body == json.dumps(update_account).encode('utf-8')
