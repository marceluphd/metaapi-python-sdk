from .clients.metatraderAccount_client import MetatraderAccountClient, MetatraderAccountDto, \
    MetatraderAccountUpdateDto
from .clients.metaApiWebsocket_client import MetaApiWebsocketClient
from .clients.timeoutException import TimeoutException
from .metaApiConnection import MetaApiConnection
from .metatraderAccountModel import MetatraderAccountModel
from .historyStorage import HistoryStorage
from datetime import datetime, timedelta
import asyncio


class MetatraderAccount(MetatraderAccountModel):
    """Implements a MetaTrader account entity"""

    def __init__(self, data: MetatraderAccountDto, metatrader_account_client: MetatraderAccountClient,
                 meta_api_websocket_client: MetaApiWebsocketClient):
        """Inits a MetaTrader account entity.

        Args:
            data: MetaTrader account data.
            metatrader_account_client: MetaTrader account REST API client.
            meta_api_websocket_client: MetaApi websocket client.
        """
        self._data = data
        self._metatraderAccountClient = metatrader_account_client
        self._metaApiWebsocketClient = meta_api_websocket_client

    @property
    def id(self) -> str:
        """Returns account id.

        Returns:
            Account id.
        """
        return self._data['_id']

    @property
    def name(self) -> str:
        """Returns account name.

        Returns:
            Account name.
        """
        return self._data['name']

    @property
    def type(self) -> str:
        """Returns account type. Possible values are cloud and self-hosted.

        Returns:
            Account type.
        """
        return self._data['type']

    @property
    def login(self) -> str:
        """Returns account login.

        Returns:
            Account login.
        """
        return self._data['login']

    @property
    def server(self) -> str:
        """Returns MetaTrader server which hosts the account.

        Returns:
            MetaTrader server which hosts the account.
        """
        return self._data['server']

    @property
    def synchronization_mode(self) -> str:
        """Returns synchronization mode, can be automatic or user. See
        https://metaapi.cloud/docs/client/websocket/synchronizationMode/ for more details.

        Returns:
            Synchronization mode.
        """
        return self._data['synchronizationMode']

    @property
    def provisioning_profile_id(self) -> str:
        """Returns id of the account's provisioning profile.

        Returns:
            Id of the account's provisioning profile.
        """
        return self._data['provisioningProfileId']

    @property
    def time_converter(self) -> str:
        """Returns algorithm used to parse your broker timezone. Supported values are icmarkets for
        America/New_York DST switch and roboforex for EET DST switch (the values will be changed soon)

        Returns:
            Algorithm used to parse your broker timezone.
        """
        return self._data['timeConverter']

    @property
    def application(self) -> str:
        """Returns application name to connect the account to. Currently allowed values are MetaApi and AgiliumTrade.

        Returns:
            Application name to connect the account to.
        """
        return self._data['application']

    @property
    def magic(self) -> int:
        """Returns MetaTrader magic to place trades using.

        Returns:
            MetaTrader magic to place trades using.
        """
        return self._data['magic']

    @property
    def state(self) -> str:
        """Returns account deployment state. One of CREATED, DEPLOYING, DEPLOYED, UNDEPLOYING, UNDEPLOYED, DELETING

        Returns:
            Account deployment state.
        """
        return self._data['state']

    @property
    def connection_status(self) -> str:
        """Returns terminal & broker connection status, one of CONNECTED, DISCONNECTED, DISCONNECTED_FROM_BROKER

        Returns:
            Terminal & broker connection status.
        """
        return self._data['connectionStatus']

    @property
    def access_token(self) -> str:
        """Returns authorization access token to be used for accessing single account data.
        Intended to be used in browser API.

        Returns:
            Authorization token.
        """
        return self._data['accessToken']

    async def reload(self):
        """Reloads MetaTrader account from API.

        Returns:
            A coroutine resolving when MetaTrader account is updated.
        """
        self._data = await self._metatraderAccountClient.get_account(self.id)

    async def remove(self):
        """Removes MetaTrader account. Cloud account transitions to DELETING state.
        It takes some time for an account to be eventually deleted. Self-hosted account is deleted immediately.

        Returns:
            A coroutine resolving when account is scheduled for deletion.
        """
        await self._metatraderAccountClient.delete_account(self.id)
        if self.type != 'self-hosted':
            try:
                await self.reload()
            except Exception as err:
                if err.__class__.__name__ != 'NotFoundException':
                    raise err

    async def deploy(self):
        """Schedules account for deployment. It takes some time for API server to be started and account to reach the
        DEPLOYED state.

        Returns:
            A coroutine resolving when account is scheduled for deployment.
        """
        await self._metatraderAccountClient.deploy_account(self.id)
        await self.reload()

    async def undeploy(self):
        """Schedules account for undeployment. It takes some time for API server to be stopped and account to reach the
        UNDEPLOYED state.

        Returns:
            A coroutine resolving when account is scheduled for undeployment.
        """
        await self._metatraderAccountClient.undeploy_account(self.id)
        await self.reload()

    async def redeploy(self):
        """Schedules account for redeployment. It takes some time for API server to be restarted and account to reach
        the DEPLOYED state.

        Returns:
            A coroutine resolving when account is scheduled for redeployment.
        """
        await self._metatraderAccountClient.redeploy_account(self.id)
        await self.reload()

    async def wait_deployed(self, timeout_in_seconds=300, interval_in_milliseconds=1000):
        """Waits until API server has finished deployment and account reached the DEPLOYED state.

        Args:
            timeout_in_seconds: Wait timeout in seconds, default is 5m.
            interval_in_milliseconds: Interval between account reloads while waiting for a change, default is 1s.

        Returns:
            A coroutine which resolves when account is deployed.

        Raises:
            TimeoutException: If account has not reached the DEPLOYED state within timeout allowed.
        """
        start_time = datetime.now()
        await self.reload()
        while self.state != 'DEPLOYED' and (start_time + timedelta(seconds=timeout_in_seconds) > datetime.now()):
            await self._delay(interval_in_milliseconds)
            await self.reload()
        if self.state != 'DEPLOYED':
            raise TimeoutException('Timed out waiting for account ' + self.id + ' to be deployed')

    async def wait_undeployed(self, timeout_in_seconds=300, interval_in_milliseconds=1000):
        """Waits until API server has finished undeployment and account reached the UNDEPLOYED state.

        Args:
            timeout_in_seconds: Wait timeout in seconds, default is 5m.
            interval_in_milliseconds: Interval between account reloads while waiting for a change, default is 1s.

        Returns:
            A coroutine which resolves when account is undeployed.

        Raises:
            TimeoutException: If account have not reached the UNDEPLOYED state within timeout allowed.
        """
        start_time = datetime.now()
        await self.reload()
        while self.state != 'UNDEPLOYED' and (start_time + timedelta(seconds=timeout_in_seconds) > datetime.now()):
            await self._delay(interval_in_milliseconds)
            await self.reload()
        if self.state != 'UNDEPLOYED':
            raise TimeoutException('Timed out waiting for account ' + self.id + ' to be undeployed')

    async def wait_removed(self, timeout_in_seconds=300, interval_in_milliseconds=1000):
        """Waits until account has been deleted.

        Args:
            timeout_in_seconds: Wait timeout in seconds, default is 5m.
            interval_in_milliseconds: Interval between account reloads while waiting for a change, default is 1s.

        Returns:
            A coroutine which resolves when account is deleted.

        Raises:
            TimeoutException: If account was not deleted within timeout allowed.
        """
        start_time = datetime.now()
        try:
            await self.reload()
            while (start_time + timedelta(seconds=timeout_in_seconds)) > datetime.now():
                await self._delay(interval_in_milliseconds)
                await self.reload()
            raise TimeoutException('Timed out waiting for account ' + self.id + ' to be deleted')
        except Exception as err:
            if err.__class__.__name__ == 'NotFoundException':
                return
            else:
                raise err

    async def wait_connected(self, timeout_in_seconds=300, interval_in_milliseconds=1000):
        """Waits until API server has connected to the terminal and terminal has connected to the broker.

        Args:
            timeout_in_seconds: Wait timeout in seconds, default is 5m
            interval_in_milliseconds: Interval between account reloads while waiting for a change, default is 1s.

        Returns:
            A coroutine which resolves when API server is connected to the broker.

        Raises:
            TimeoutException: If account has not connected to the broker within timeout allowed.
        """
        start_time = datetime.now()
        await self.reload()
        while self.connection_status != 'CONNECTED' and (start_time +
                                                         timedelta(seconds=timeout_in_seconds)) > datetime.now():
            await self._delay(interval_in_milliseconds)
            await self.reload()
        if self.connection_status != 'CONNECTED':
            raise TimeoutException('Timed out waiting for account ' + self.id + ' to connect to the broker')

    async def connect(self, history_storage: HistoryStorage = None) -> MetaApiConnection:
        """Connects to MetaApi.

        Args:
            history_storage: optional history storage

        Returns:
            MetaApi connection.
        """
        connection = MetaApiConnection(self._metaApiWebsocketClient, self, history_storage)
        await connection.subscribe()
        return connection

    async def update(self, account: MetatraderAccountUpdateDto):
        """Updates MetaTrader account data.

        Args:
            account: MetaTrader account update.

        Returns:
            A coroutine resolving when account is updated.
        """
        await self._metatraderAccountClient.update_account(self.id, account)
        await self.reload()

    async def _delay(self, timeout_in_milliseconds):
        await asyncio.sleep(timeout_in_milliseconds / 1000)
