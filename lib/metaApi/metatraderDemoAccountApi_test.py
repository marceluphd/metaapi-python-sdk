from mock import AsyncMock, MagicMock
from ..clients.metaApi.metatraderDemoAccount_client import MetatraderDemoAccountClient, NewMT4DemoAccount, \
    NewMT5DemoAccount, MetatraderDemoAccountDto
from .metatraderDemoAccountApi import MetatraderDemoAccountApi
from .metatraderDemoAccount import MetatraderDemoAccount
import pytest


class MockClient(MetatraderDemoAccountClient):
    def create_mt4_demo_account(self, profile_id: str, account: NewMT4DemoAccount) -> MetatraderDemoAccountDto:
        pass

    def create_mt5_demo_account(self, profile_id: str, account: NewMT5DemoAccount) -> MetatraderDemoAccountDto:
        pass


client = MockClient(MagicMock(), MagicMock())
api = MetatraderDemoAccountApi(client)


@pytest.fixture(autouse=True)
async def run_around_tests():
    global api
    api = MetatraderDemoAccountApi(client)
    yield


class TestMetatraderAccountApi:
    @pytest.mark.asyncio
    async def test_create_mt4(self):
        """Should create MT4 demo account."""
        expected = {
            'login': '12345',
            'password': 'qwerty',
            'serverName': 'HugosWay-Demo3',
            'investorPassword': 'qwerty'
        }
        client.create_mt4_demo_account = AsyncMock(return_value=expected)
        api = MetatraderDemoAccountApi(client)
        new_account_data = {
            'balance': 10,
            'email': 'test@test.com',
            'leverage': 15,
            'serverName': 'server'
        }
        account = await api.create_mt4_demo_account('profileId1', new_account_data)
        assert account.login == expected['login']
        assert account.password == expected['password']
        assert account.server_name == expected['serverName']
        assert account.investor_password == expected['investorPassword']
        assert isinstance(account, MetatraderDemoAccount)
        client.create_mt4_demo_account.assert_called_with('profileId1', new_account_data)

    @pytest.mark.asyncio
    async def test_create_mt5(self):
        """Should create MT5 demo account."""
        expected = {
            'login': '12345',
            'password': 'qwerty',
            'serverName': 'HugosWay-Demo3',
            'investorPassword': 'qwerty'
        }
        client.create_mt5_demo_account = AsyncMock(return_value=expected)
        api = MetatraderDemoAccountApi(client)
        new_account_data = {
            'balance': 10,
            'email': 'test@test.com',
            'leverage': 15,
            'serverName': 'server'
        }
        account = await api.create_mt5_demo_account('profileId2', new_account_data)
        assert account.login == expected['login']
        assert account.password == expected['password']
        assert account.server_name == expected['serverName']
        assert account.investor_password == expected['investorPassword']
        assert isinstance(account, MetatraderDemoAccount)
        client.create_mt5_demo_account.assert_called_with('profileId2', new_account_data)
