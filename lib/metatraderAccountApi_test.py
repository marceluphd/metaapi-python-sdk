from .metatraderAccountApi import MetatraderAccountApi
from .metatraderAccount import MetatraderAccount
from .clients.errorHandler import NotFoundException
from .clients.metaApiWebsocket_client import MetaApiWebsocketClient
from .clients.metatraderAccount_client import MetatraderAccountClient, NewMetatraderAccountDto
from .metaApiConnection import MetaApiConnection
from .clients.reconnectListener import ReconnectListener
from .memoryHistoryStorage import MemoryHistoryStorage
from mock import AsyncMock, MagicMock
from requests import Response
from datetime import datetime
from .models import date
import pytest


class MockClient(MetatraderAccountClient):
    def get_accounts(self, provisioning_profile_id: str = None) -> Response:
        pass

    def get_account(self, id: str) -> Response:
        pass

    def create_account(self, account: NewMetatraderAccountDto) -> Response:
        pass

    def delete_account(self, id: str) -> Response:
        pass

    def deploy_account(self, id: str) -> Response:
        pass

    def undeploy_account(self, id: str) -> Response:
        pass

    def redeploy_account(self, id: str) -> Response:
        pass


class MockWebsocketClient(MetaApiWebsocketClient):
    def add_synchronization_listener(self, account_id: str, listener):
        pass

    def add_reconnect_listener(self, listener: ReconnectListener):
        pass

    def subscribe(self, account_id: str):
        pass


class MockStorage(MemoryHistoryStorage):
    async def last_history_order_time(self) -> datetime:
        return date('2020-01-01T00:00:00.000Z')

    async def last_deal_time(self) -> datetime:
        return date('2020-01-02T00:00:00.000Z')


client = MockClient(MagicMock(), MagicMock())
websocket_client = MockWebsocketClient('token')
api = MetatraderAccountApi(client, websocket_client)


class TestMetatraderAccountApi:
    @pytest.mark.asyncio
    async def test_retrive_mt_accounts(self):
        """Should retrieve MT accounts."""
        client.get_accounts = AsyncMock(return_value=[{'_id': 'id'}])
        accounts = await api.get_accounts('profileId')
        assert list(map(lambda a: a.id, accounts)) == ['id']
        for account in accounts:
            assert isinstance(account, MetatraderAccount)
        client.get_accounts.assert_called_with('profileId')

    @pytest.mark.asyncio
    async def test_retrive_mt_account_by_id(self):
        """Should retrieve MT account by id."""
        client.get_account = AsyncMock(return_value={
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
            'type': 'cloud',
            'accessToken': '2RUnoH1ldGbnEneCoqRTgI4QO1XOmVzbH5EVoQsA'
        })
        account = await api.get_account('id')
        assert account.id == 'id'
        assert account.login == '50194988'
        assert account.name == 'mt5a'
        assert account.server == 'ICMarketsSC-Demo'
        assert account.provisioning_profile_id == 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076'
        assert account.magic == 123456
        assert account.time_converter == 'icmarkets'
        assert account.application == 'MetaApi'
        assert account.connection_status == 'DISCONNECTED'
        assert account.state == 'DEPLOYED'
        assert account.synchronization_mode == 'automatic'
        assert account.type == 'cloud'
        assert account.access_token == '2RUnoH1ldGbnEneCoqRTgI4QO1XOmVzbH5EVoQsA'
        assert isinstance(account, MetatraderAccount)
        client.get_account.assert_called_with('id')

    @pytest.mark.asyncio
    async def test_create_mt_account(self):
        """Should create MT account."""
        client.create_account = AsyncMock(return_value={'id': 'id'})
        client.get_account = AsyncMock(return_value={
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
          'type': 'cloud',
          'accessToken': '2RUnoH1ldGbnEneCoqRTgI4QO1XOmVzbH5EVoQsA'
        })
        new_account_data = {
            'login': '50194988',
            'password': 'Test1234',
            'name': 'mt5a',
            'server': 'ICMarketsSC-Demo',
            'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
            'magic': 123456,
            'timeConverter': 'icmarkets',
            'application': 'MetaApi',
            'synchronizationMode': 'automatic',
            'type': 'cloud',
            'accessToken': 'NyV5no9TMffJyUts2FjI80wly0so3rVCz4xOqiDx'
        }
        account = await api.create_account(new_account_data)
        assert account.id == 'id'
        assert account.login == '50194988'
        assert account.name == 'mt5a'
        assert account.server == 'ICMarketsSC-Demo'
        assert account.provisioning_profile_id == 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076'
        assert account.magic == 123456
        assert account.time_converter == 'icmarkets'
        assert account.application == 'MetaApi'
        assert account.connection_status == 'DISCONNECTED'
        assert account.state == 'DEPLOYED'
        assert account.synchronization_mode == 'automatic'
        assert account.type == 'cloud'
        assert account.access_token == '2RUnoH1ldGbnEneCoqRTgI4QO1XOmVzbH5EVoQsA'
        assert isinstance(account, MetatraderAccount)
        client.create_account.assert_called_with(new_account_data)
        client.get_account.assert_called_with('id')

    @pytest.mark.asyncio
    async def test_reload_mt_account(self):
        """Should reload MT account."""
        client.get_account = AsyncMock(side_effect=[{
            '_id': 'id',
            'login': '50194988',
            'name': 'mt5a',
            'server': 'ICMarketsSC-Demo',
            'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
            'magic': 123456,
            'timeConverter': 'icmarkets',
            'application': 'MetaApi',
            'connectionStatus': 'DISCONNECTED',
            'state': 'DEPLOYING',
            'synchronizationMode': 'automatic',
            'type': 'cloud'
          },
            {
                '_id': 'id',
                'login': '50194988',
                'name': 'mt5a',
                'server': 'ICMarketsSC-Demo',
                'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
                'magic': 123456,
                'timeConverter': 'icmarkets',
                'application': 'MetaApi',
                'connectionStatus': 'CONNECTED',
                'state': 'DEPLOYED',
                'synchronizationMode': 'automatic',
                'type': 'cloud'
            }])
        account = await api.get_account('id')
        await account.reload()
        assert account.connection_status == 'CONNECTED'
        assert account.state == 'DEPLOYED'
        client.get_account.assert_called_with('id')
        assert client.get_account.call_count == 2

    @pytest.mark.asyncio
    async def test_remove_mt_account(self):
        """Should remove MT account."""
        client.get_account = AsyncMock(side_effect=[{
            '_id': 'id',
            'login': '50194988',
            'name': 'mt5a',
            'server': 'ICMarketsSC-Demo',
            'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
            'magic': 123456,
            'timeConverter': 'icmarkets',
            'application': 'MetaApi',
            'connectionStatus': 'CONNECTED',
            'state': 'DEPLOYED',
            'synchronizationMode': 'automatic',
            'type': 'cloud'
          },
            {
                '_id': 'id',
                'login': '50194988',
                'name': 'mt5a',
                'server': 'ICMarketsSC-Demo',
                'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
                'magic': 123456,
                'timeConverter': 'icmarkets',
                'application': 'MetaApi',
                'connectionStatus': 'CONNECTED',
                'state': 'DELETING',
                'synchronizationMode': 'automatic',
                'type': 'cloud'
            }
        ])
        client.delete_account = AsyncMock()
        account = await api.get_account('id')
        await account.remove()
        assert account.state == 'DELETING'
        client.delete_account.assert_called_with('id')
        client.get_account.assert_called_with('id')
        assert client.get_account.call_count == 2

    @pytest.mark.asyncio
    async def test_deploy_mt_account(self):
        """Should deploy MT account."""
        client.get_account = AsyncMock(side_effect=[{
            '_id': 'id',
            'login': '50194988',
            'name': 'mt5a',
            'server': 'ICMarketsSC-Demo',
            'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
            'magic': 123456,
            'timeConverter': 'icmarkets',
            'application': 'MetaApi',
            'connectionStatus': 'DISCONNECTED',
            'state': 'UNDEPLOYED',
            'synchronizationMode': 'automatic',
            'type': 'cloud'
          }, {
                '_id': 'id',
                'login': '50194988',
                'name': 'mt5a',
                'server': 'ICMarketsSC-Demo',
                'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
                'magic': 123456,
                'timeConverter': 'icmarkets',
                'application': 'MetaApi',
                'connectionStatus': 'CONNECTED',
                'state': 'DEPLOYING',
                'synchronizationMode': 'automatic',
                'type': 'cloud'
        }])
        client.deploy_account = AsyncMock()
        account = await api.get_account('id')
        await account.deploy()
        assert account.state == 'DEPLOYING'
        client.deploy_account.assert_called_with('id')
        client.get_account.assert_called_with('id')
        assert client.get_account.call_count == 2

    @pytest.mark.asyncio
    async def test_undeploy_mt_account(self):
        """Should undeploy MT account."""
        client.get_account = AsyncMock(side_effect=[{
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
          }, {
            '_id': 'id',
            'login': '50194988',
            'name': 'mt5a',
            'server': 'ICMarketsSC-Demo',
            'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
            'magic': 123456,
            'timeConverter': 'icmarkets',
            'application': 'MetaApi',
            'connectionStatus': 'CONNECTED',
            'state': 'UNDEPLOYING',
            'synchronizationMode': 'automatic',
            'type': 'cloud'
        }])
        client.undeploy_account = AsyncMock()
        account = await api.get_account('id')
        await account.undeploy()
        assert account.state == 'UNDEPLOYING'
        client.undeploy_account.assert_called_with('id')
        client.get_account.assert_called_with('id')
        assert client.get_account.call_count == 2

    @pytest.mark.asyncio
    async def test_redeploy_mt_account(self):
        """Should redeploy MT account."""
        client.get_account = AsyncMock(side_effect=[{
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
          }, {
            '_id': 'id',
            'login': '50194988',
            'name': 'mt5a',
            'server': 'ICMarketsSC-Demo',
            'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
            'magic': 123456,
            'timeConverter': 'icmarkets',
            'application': 'MetaApi',
            'connectionStatus': 'CONNECTED',
            'state': 'UNDEPLOYING',
            'synchronizationMode': 'automatic',
            'type': 'cloud'
          }])
        client.redeploy_account = AsyncMock()
        account = await api.get_account('id')
        await account.redeploy()
        assert account.state == 'UNDEPLOYING'
        client.redeploy_account.assert_called_with('id')
        client.get_account.assert_called_with('id')
        assert client.get_account.call_count == 2

    @pytest.mark.asyncio
    async def test_wait_for_deployment(self):
        """Should wait for deployment."""
        deploying_account = {
            '_id': 'id',
            'login': '50194988',
            'name': 'mt5a',
            'server': 'ICMarketsSC-Demo',
            'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
            'magic': 123456,
            'timeConverter': 'icmarkets',
            'application': 'MetaApi',
            'connectionStatus': 'DISCONNECTED',
            'state': 'DEPLOYING',
            'synchronizationMode': 'automatic',
            'type': 'cloud'
        }
        client.get_account = AsyncMock(side_effect=[deploying_account, deploying_account,
                                                    {
                                                        '_id': 'id',
                                                        'login': '50194988',
                                                        'name': 'mt5a',
                                                        'server': 'ICMarketsSC-Demo',
                                                        'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
                                                        'magic': 123456,
                                                        'timeConverter': 'icmarkets',
                                                        'application': 'MetaApi',
                                                        'connectionStatus': 'CONNECTED',
                                                        'state': 'DEPLOYED',
                                                        'synchronizationMode': 'automatic',
                                                        'type': 'cloud'
                                                    }
                                                    ])
        account = await api.get_account('id')
        await account.wait_deployed(1, 50)
        assert account.state == 'DEPLOYED'
        client.get_account.assert_called_with('id')
        assert client.get_account.call_count == 3

    @pytest.mark.asyncio
    async def test_time_out_deployment(self):
        """Should time out waiting for deployment."""
        deploying_account = {
            '_id': 'id',
            'login': '50194988',
            'name': 'mt5a',
            'server': 'ICMarketsSC-Demo',
            'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
            'magic': 123456,
            'timeConverter': 'icmarkets',
            'application': 'MetaApi',
            'connectionStatus': 'DISCONNECTED',
            'state': 'DEPLOYING',
            'synchronizationMode': 'automatic',
            'type': 'cloud'
        }
        client.get_account = AsyncMock(return_value=deploying_account)
        account = await api.get_account('id')
        try:
            await account.wait_deployed(1, 50)
            raise Exception('TimeoutError is expected')
        except Exception as err:
            assert err.__class__.__name__ == 'TimeoutException'
            assert account.state == 'DEPLOYING'
        client.get_account.assert_called_with('id')

    @pytest.mark.asyncio
    async def test_wait_for_undeployment(self):
        """Should wait for undeployment."""
        undeploying_account = {
            '_id': 'id',
            'login': '50194988',
            'name': 'mt5a',
            'server': 'ICMarketsSC-Demo',
            'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
            'magic': 123456,
            'timeConverter': 'icmarkets',
            'application': 'MetaApi',
            'connectionStatus': 'DISCONNECTED',
            'state': 'UNDEPLOYING',
            'synchronizationMode': 'automatic',
            'type': 'cloud'
        }
        client.get_account = AsyncMock(side_effect=[undeploying_account, undeploying_account,
                                                    {
                                                        '_id': 'id',
                                                        'login': '50194988',
                                                        'name': 'mt5a',
                                                        'server': 'ICMarketsSC-Demo',
                                                        'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
                                                        'magic': 123456,
                                                        'timeConverter': 'icmarkets',
                                                        'application': 'MetaApi',
                                                        'connectionStatus': 'CONNECTED',
                                                        'state': 'UNDEPLOYED',
                                                        'synchronizationMode': 'automatic',
                                                        'type': 'cloud'
                                                    }
                                                    ])
        account = await api.get_account('id')
        await account.wait_undeployed(1, 50)
        assert account.state == 'UNDEPLOYED'
        client.get_account.assert_called_with('id')
        assert client.get_account.call_count == 3

    @pytest.mark.asyncio
    async def test_time_out_undeployment(self):
        """Should wait for undeployment."""
        undeploying_account = {
            '_id': 'id',
            'login': '50194988',
            'name': 'mt5a',
            'server': 'ICMarketsSC-Demo',
            'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
            'magic': 123456,
            'timeConverter': 'icmarkets',
            'application': 'MetaApi',
            'connectionStatus': 'DISCONNECTED',
            'state': 'UNDEPLOYING',
            'synchronizationMode': 'automatic',
            'type': 'cloud'
        }
        client.get_account = AsyncMock(return_value=undeploying_account)
        account = await api.get_account('id')
        try:
            await account.wait_undeployed(1, 50)
            raise Exception('TimeoutException is expected')
        except Exception as err:
            assert err.__class__.__name__ == 'TimeoutException'
            assert account.state == 'UNDEPLOYING'
        client.get_account.assert_called_with('id')

    @pytest.mark.asyncio
    async def test_wait_until_removed(self):
        """Should wait until removed."""
        deleting_account = {
            '_id': 'id',
            'login': '50194988',
            'name': 'mt5a',
            'server': 'ICMarketsSC-Demo',
            'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
            'magic': 123456,
            'timeConverter': 'icmarkets',
            'application': 'MetaApi',
            'connectionStatus': 'DISCONNECTED',
            'state': 'DELETING',
            'synchronizationMode': 'automatic',
            'type': 'cloud'
          }
        client.get_account = AsyncMock(side_effect=[deleting_account, deleting_account, NotFoundException('')])
        account = await api.get_account('id')
        await account.wait_removed(1, 50)
        client.get_account.assert_called_with('id')
        assert client.get_account.call_count == 3

    @pytest.mark.asyncio
    async def test_time_out_waiting_until_removed(self):
        """Should wait until removed."""
        deleting_account = {
            '_id': 'id',
            'login': '50194988',
            'name': 'mt5a',
            'server': 'ICMarketsSC-Demo',
            'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
            'magic': 123456,
            'timeConverter': 'icmarkets',
            'application': 'MetaApi',
            'connectionStatus': 'DISCONNECTED',
            'state': 'DELETING',
            'synchronizationMode': 'automatic',
            'type': 'cloud'
        }
        client.get_account = AsyncMock(return_value=deleting_account)
        account = await api.get_account('id')
        try:
            await account.wait_removed(1, 50)
            raise Exception('TimeoutException is expected')
        except Exception as err:
            assert err.__class__.__name__ == 'TimeoutException'
        client.get_account.assert_called_with('id')

    @pytest.mark.asyncio
    async def test_wait_until_broker_connection(self):
        """Should wait util broker connection."""
        disconnected_account = {
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
        client.get_account = AsyncMock(side_effect=[disconnected_account, disconnected_account,
                                                    {
                                                        '_id': 'id',
                                                        'login': '50194988',
                                                        'name': 'mt5a',
                                                        'server': 'ICMarketsSC-Demo',
                                                        'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
                                                        'magic': 123456,
                                                        'timeConverter': 'icmarkets',
                                                        'application': 'MetaApi',
                                                        'connectionStatus': 'CONNECTED',
                                                        'state': 'DEPLOYED',
                                                        'synchronizationMode': 'automatic',
                                                        'type': 'cloud'
                                                    }])
        account = await api.get_account('id')
        await account.wait_connected(1, 50)
        assert account.connection_status == 'CONNECTED'
        client.get_account.assert_called_with('id')
        assert client.get_account.call_count == 3

    @pytest.mark.asyncio
    async def test_time_out_waiting_for_broker_connection(self):
        """Should time out waiting for broker connection."""
        disconnected_account = {
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
        client.get_account = AsyncMock(return_value=disconnected_account)
        account = await api.get_account('id')
        try:
            await account.wait_connected(1, 50)
            raise Exception('TimeoutException is expected')
        except Exception as err:
            assert err.__class__.__name__ == 'TimeoutException'
            assert account.connection_status == 'DISCONNECTED'
        client.get_account.assert_called_with('id')

    @pytest.mark.asyncio
    async def test_connect_to_mt_terminal(self):
        """Should connect to an MT terminal."""
        websocket_client.add_synchronization_listener = MagicMock()
        websocket_client.subscribe = AsyncMock()
        client.get_account = AsyncMock(return_value={'_id': 'id', 'synchronizationMode': 'user'})
        account = await api.get_account('id')
        storage = MockStorage()
        connection = await account.connect(storage)
        assert isinstance(connection, MetaApiConnection)
        assert connection.history_storage == storage
        websocket_client.add_synchronization_listener.assert_called_with('id', storage)
        websocket_client.subscribe.assert_called_with('id')

    @pytest.mark.asyncio
    async def test_update_mt_account(self):
        """Should update MT account."""
        client.get_account = AsyncMock(side_effect=[{
            '_id': 'id',
            'login': '50194988',
            'name': 'mt5a',
            'server': 'ICMarketsSC-Demo',
            'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
            'magic': 123456,
            'timeConverter': 'icmarkets',
            'application': 'MetaApi',
            'connectionStatus': 'CONNECTED',
            'state': 'DEPLOYED',
            'synchronizationMode': 'automatic',
            'type': 'cloud'
          }, {
            '_id': 'id',
            'login': '50194988',
            'name': 'mt5a__',
            'server': 'OtherMarkets-Demo',
            'provisioningProfileId': 'f9ce1f12-e720-4b9a-9477-c2d4cb25f076',
            'magic': 123456,
            'timeConverter': 'icmarkets',
            'application': 'MetaApi',
            'connectionStatus': 'CONNECTED',
            'state': 'DEPLOYED',
            'synchronizationMode': 'user',
            'type': 'cloud'
          }])
        client.update_account = AsyncMock()
        account = await api.get_account('id')
        await account.update({
          'name': 'mt5a__',
          'password': 'moreSecurePass',
          'server': 'OtherMarkets-Demo',
          'synchronizationMode': 'user'
        })
        assert account.name == 'mt5a__'
        assert account.server == 'OtherMarkets-Demo'
        assert account.synchronization_mode == 'user'
        client.update_account.assert_called_with('id', {
          'name': 'mt5a__',
          'password': 'moreSecurePass',
          'server': 'OtherMarkets-Demo',
          'synchronizationMode': 'user'
        })
        client.get_account.assert_called_with('id')
        assert client.get_account.call_count == 2
