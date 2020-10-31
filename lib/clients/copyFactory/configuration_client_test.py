from ..httpClient import HttpClient
from .configuration_client import ConfigurationClient
from ...metaApi.models import date
import pytest
import responses
import json
from mock import AsyncMock
from copy import deepcopy

copy_factory_api_url = 'https://trading-api-v1.agiliumtrade.agiliumtrade.ai'
http_client = HttpClient()
copy_factory_client = ConfigurationClient(http_client, 'header.payload.sign')


@pytest.fixture(autouse=True)
async def run_around_tests():
    global http_client
    global copy_factory_client
    http_client = HttpClient()
    copy_factory_client = ConfigurationClient(http_client, 'header.payload.sign')


class TestConfigurationClient:
    @pytest.mark.asyncio
    async def test_generate_account_id(self):
        """Should generate account id."""
        assert len(copy_factory_client.generate_account_id()) == 64

    @pytest.mark.asyncio
    async def test_update_copyfactory_account(self):
        """Should update CopyFactory account via API."""
        account = {
            'name': 'Demo account',
            'connectionId': 'e8867baa-5ec2-45ae-9930-4d5cea18d0d6',
            'reservedMarginFraction': 0.25,
            'subscriptions': [
                {
                    'strategyId': 'ABCD',
                    'multiplier': 1
                }
            ]
        }
        with responses.RequestsMock() as rsps:
            rsps.add(responses.PUT, f'{copy_factory_api_url}/users/current/configuration/accounts/' +
                                    '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
                     json=account, status=200)

            await copy_factory_client.update_account('0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
                                                     account)
            assert rsps.calls[0].request.url == f'{copy_factory_api_url}/users/current/configuration/accounts/' + \
                                                '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
            assert rsps.calls[0].request.method == 'PUT'
            assert rsps.calls[0].request.headers['auth-token'] == 'header.payload.sign'
            assert rsps.calls[0].request.body == json.dumps(account).encode('utf-8')

    @pytest.mark.asyncio
    async def test_not_update_copyfactory_account_with_account_token(self):
        """Should not update CopyFactory account via API with account token."""
        copy_factory_client = ConfigurationClient(http_client, 'token')
        try:
            await copy_factory_client.update_account('id', {})
        except Exception as err:
            assert err.__str__() == 'You can not invoke update_account method, because you have connected with ' + \
                                    'account access token. Please use API access token from ' + \
                                    'https://app.metaapi.cloud/token page to invoke this method.'

    @pytest.mark.asyncio
    async def test_retrieve_copyfactory_accounts_from_api(self):
        """Should retrieve CopyFactory accounts from API."""
        expected = [{
          '_id': '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
          'subscriberId': 'subscriberId',
          'name': 'Demo account',
          'connectionId': 'e8867baa-5ec2-45ae-9930-4d5cea18d0d6',
          'reservedMarginFraction': 0.25,
          'subscriptions': [
            {
              'strategyId': 'ABCD',
              'multiplier': 1
            }
          ]
        }]
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{copy_factory_api_url}/users/current/configuration/accounts',
                     json=expected, status=200)
            accounts = await copy_factory_client.get_accounts()
            assert rsps.calls[0].request.url == f'{copy_factory_api_url}/users/current/configuration/accounts'
            assert rsps.calls[0].request.method == 'GET'
            assert rsps.calls[0].request.headers['auth-token'] == 'header.payload.sign'
            assert accounts == expected

    @pytest.mark.asyncio
    async def test_not_retrieve_copyfactory_accounts_with_account_token(self):
        """Should not retrieve CopyFactory accounts from API with account token."""
        copy_factory_client = ConfigurationClient(http_client, 'token')
        try:
            await copy_factory_client.get_accounts()
        except Exception as err:
            assert err.__str__() == 'You can not invoke get_accounts method, because you have connected with ' + \
                                    'account access token. Please use API access token from ' + \
                                    'https://app.metaapi.cloud/token page to invoke this method.'

    @pytest.mark.asyncio
    async def test_remove_copyfactory_account(self):
        """Should remove CopyFactory account via API."""
        with responses.RequestsMock() as rsps:
            rsps.add(responses.DELETE, f'{copy_factory_api_url}/users/current/configuration/accounts/' +
                     '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef', status=204)
            await copy_factory_client\
                .remove_account('0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef')
            assert rsps.calls[0].request.url == f'{copy_factory_api_url}/users/current/configuration/accounts/' + \
                   '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
            assert rsps.calls[0].request.method == 'DELETE'
            assert rsps.calls[0].request.headers['auth-token'] == 'header.payload.sign'

    @pytest.mark.asyncio
    async def test_not_remove_copyfactory_account_with_account_token(self):
        """Should not remove CopyFactory account via API with account token."""
        copy_factory_client = ConfigurationClient(http_client, 'token')
        try:
            await copy_factory_client.remove_account('id')
        except Exception as err:
            assert err.__str__() == 'You can not invoke remove_account method, because you have connected with ' + \
                                    'account access token. Please use API access token from ' + \
                                    'https://app.metaapi.cloud/token page to invoke this method.'

    @pytest.mark.asyncio
    async def test_generate_strategy_id(self):
        """Should retrieve CopyFactory accounts from API."""
        expected = {
            'id': 'ABCD'
        }
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{copy_factory_api_url}/users/current/configuration/unused-strategy-id',
                     json=expected, status=200)
            id = await copy_factory_client.generate_strategy_id()
            assert rsps.calls[0].request.url == f'{copy_factory_api_url}/users/current/configuration/unused-strategy-id'
            assert rsps.calls[0].request.method == 'GET'
            assert rsps.calls[0].request.headers['auth-token'] == 'header.payload.sign'
            assert id == expected

    @pytest.mark.asyncio
    async def test_not_generate_strategy_id_with_account_token(self):
        """Should not generate strategy id with account token."""
        copy_factory_client = ConfigurationClient(http_client, 'token')
        try:
            await copy_factory_client.generate_strategy_id()
        except Exception as err:
            assert err.__str__() == 'You can not invoke generate_strategy_id method, because you have connected ' + \
                   'with account access token. Please use API access token from ' + \
                   'https://app.metaapi.cloud/token page to invoke this method.'

    @pytest.mark.asyncio
    async def test_update_strategy(self):
        """Should update strategy via API."""
        strategy = {
            'name': 'Test strategy',
            'positionLifecycle': 'hedging',
            'connectionId': 'e8867baa-5ec2-45ae-9930-4d5cea18d0d6',
            'maxTradeRisk': 0.1,
            'stopOutRisk': {
                'value': 0.4,
                'startTime': '2020-08-24T00:00:00.000Z'
            },
            'timeSettings': {
                'lifetimeInHours': 192,
                'openingIntervalInMinutes': 5
            }
        }
        with responses.RequestsMock() as rsps:
            rsps.add(responses.PUT, f'{copy_factory_api_url}/users/current/configuration/strategies/ABCD',
                     json=strategy, status=200)

            await copy_factory_client.update_strategy('ABCD', strategy)
            assert rsps.calls[0].request.url == f'{copy_factory_api_url}/users/current/configuration/strategies/ABCD'
            assert rsps.calls[0].request.method == 'PUT'
            assert rsps.calls[0].request.headers['auth-token'] == 'header.payload.sign'
            assert rsps.calls[0].request.body == json.dumps(strategy).encode('utf-8')

    @pytest.mark.asyncio
    async def test_not_update_strategy_with_account_token(self):
        """Should not update strategy with account token."""
        copy_factory_client = ConfigurationClient(http_client, 'token')
        try:
            await copy_factory_client.update_strategy('ABCD', {})
        except Exception as err:
            assert err.__str__() == 'You can not invoke update_strategy method, because you have connected with ' + \
                                    'account access token. Please use API access token from ' + \
                                    'https://app.metaapi.cloud/token page to invoke this method.'

    @pytest.mark.asyncio
    async def test_retrieve_strategies_from_api(self):
        """Should retrieve strategies from API."""
        expected = [{
          '_id': 'ABCD',
          'providerId': 'providerId',
          'platformCommissionRate': 0.01,
          'name': 'Test strategy',
          'positionLifecycle': 'hedging',
          'connectionId': 'e8867baa-5ec2-45ae-9930-4d5cea18d0d6',
          'maxTradeRisk': 0.1,
          'stopOutRisk': {
            'value': 0.4,
            'startTime': '2020-08-24T00:00:00.000Z'
          },
          'timeSettings': {
            'lifetimeInHours': 192,
            'openingIntervalInMinutes': 5
          }
        }]
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{copy_factory_api_url}/users/current/configuration/strategies',
                     json=expected, status=200)
            strategies = await copy_factory_client.get_strategies()
            assert rsps.calls[0].request.url == f'{copy_factory_api_url}/users/current/configuration/strategies'
            assert rsps.calls[0].request.method == 'GET'
            assert rsps.calls[0].request.headers['auth-token'] == 'header.payload.sign'
            assert strategies == expected

    @pytest.mark.asyncio
    async def test_not_retrieve_strategies_with_account_token(self):
        """Should not retrieve strategies with account token."""
        copy_factory_client = ConfigurationClient(http_client, 'token')
        try:
            await copy_factory_client.get_strategies()
        except Exception as err:
            assert err.__str__() == 'You can not invoke get_strategies method, because you have connected with ' + \
                                    'account access token. Please use API access token from ' + \
                                    'https://app.metaapi.cloud/token page to invoke this method.'

    @pytest.mark.asyncio
    async def test_remove_strategy(self):
        """Should remove strategy via API."""
        with responses.RequestsMock() as rsps:
            rsps.add(responses.DELETE, f'{copy_factory_api_url}/users/current/configuration/strategies/ABCD',
                     status=204)
            await copy_factory_client.remove_strategy('ABCD')
            assert rsps.calls[0].request.url == f'{copy_factory_api_url}/users/current/configuration/strategies/ABCD'
            assert rsps.calls[0].request.method == 'DELETE'
            assert rsps.calls[0].request.headers['auth-token'] == 'header.payload.sign'

    @pytest.mark.asyncio
    async def test_not_remove_strategy_with_account_token(self):
        """Should not remove strategy with account token."""
        copy_factory_client = ConfigurationClient(http_client, 'token')
        try:
            await copy_factory_client.remove_strategy('ABCD')
        except Exception as err:
            assert err.__str__() == 'You can not invoke remove_strategy method, because you have connected with ' + \
                                    'account access token. Please use API access token from ' + \
                                    'https://app.metaapi.cloud/token page to invoke this method.'

    @pytest.mark.asyncio
    async def test_retrieve_active_resync_tasks_from_api(self):
        """Should retrieve active resynchronization tasks via API."""
        result = [{
            '_id': 'ABCD',
            'type': 'CREATE_STRATEGY',
            'createdAt': '2020-08-25T00:00:00.000Z',
            'status': 'EXECUTING'
        }]
        expected = [{
            '_id': 'ABCD',
            'type': 'CREATE_STRATEGY',
            'createdAt': date('2020-08-25T00:00:00.000Z'),
            'status': 'EXECUTING'
        }]
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{copy_factory_api_url}/users/current/configuration/connections/' +
                     'accountId/active-resynchronization-tasks', json=result, status=200)
            strategies = await copy_factory_client.get_active_resynchronization_tasks('accountId')
            assert rsps.calls[0].request.url == f'{copy_factory_api_url}/users/current/configuration/connections/' + \
                'accountId/active-resynchronization-tasks'
            assert rsps.calls[0].request.method == 'GET'
            assert rsps.calls[0].request.headers['auth-token'] == 'header.payload.sign'
            assert strategies == expected

    @pytest.mark.asyncio
    async def test_not_retrieve_resync_tasks_with_account_token(self):
        """Should not retrieve active resynchronization tasks with account token."""
        copy_factory_client = ConfigurationClient(http_client, 'token')
        try:
            await copy_factory_client.get_active_resynchronization_tasks('ABCD')
        except Exception as err:
            assert err.__str__() == 'You can not invoke get_active_resynchronization_tasks method, ' + \
                   'because you have connected with account access token. Please use API access token from ' + \
                   'https://app.metaapi.cloud/token page to invoke this method.'

    @pytest.mark.asyncio
    async def test_wait_resync_tasks(self):
        """Should wait until active resynchronization tasks are completed."""
        active_tasks = [{
            '_id': 'ABCD',
            'type': 'CREATE_STRATEGY',
            'createdAt': '2020-08-25T00:00:00.000Z',
            'status': 'EXECUTING'
        }]
        copy_factory_client._httpClient.request = AsyncMock(side_effect=[deepcopy(active_tasks),
                                                                         deepcopy(active_tasks), []])
        await copy_factory_client.wait_resynchronization_tasks_completed('accountId', 1, 50)
        copy_factory_client._httpClient.request.assert_called_with({
            'url': f"{copy_factory_api_url}/users/current/configuration/connections/accountId" +
                   "/active-resynchronization-tasks",
            'method': 'GET',
            'headers': {
                'auth-token': 'header.payload.sign'
            }
        })
        assert copy_factory_client._httpClient.request.call_count == 3

    @pytest.mark.asyncio
    async def test_timeout_resync_tasks(self):
        """Should time out waiting for active resynchronization tasks to be completed."""
        active_tasks = [{
            '_id': 'ABCD',
            'type': 'CREATE_STRATEGY',
            'createdAt': '2020-08-25T00:00:00.000Z',
            'status': 'EXECUTING'
        }]
        copy_factory_client._httpClient.request = AsyncMock(side_effect=[deepcopy(active_tasks),
                                                                         deepcopy(active_tasks),
                                                                         deepcopy(active_tasks)])
        try:
            await copy_factory_client.wait_resynchronization_tasks_completed('accountId', 0.5, 300)
            raise Exception('TimeoutException is expected')
        except Exception as err:
            assert err.__class__.__name__ == 'TimeoutException'
        copy_factory_client._httpClient.request.assert_called_with({
            'url': f"{copy_factory_api_url}/users/current/configuration/connections/accountId" +
                   "/active-resynchronization-tasks",
            'method': 'GET',
            'headers': {
                'auth-token': 'header.payload.sign'
            }
        })
