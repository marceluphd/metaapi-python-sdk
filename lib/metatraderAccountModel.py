from .historyStorage import HistoryStorage
from typing import Optional
from abc import ABC, abstractmethod


class MetatraderAccountModel(ABC):
    """Defines interface for a MetaTrader account class."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Returns account id.

        Returns:
            Account id.
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns account name.

        Returns:
            Account name.
        """

    @property
    @abstractmethod
    def type(self) -> str:
        """Returns account type. Possible values are cloud and self-hosted.

        Returns:
            Account type.
        """

    @property
    @abstractmethod
    def login(self) -> str:
        """Returns account login.

        Returns:
            Account login.
        """

    @property
    @abstractmethod
    def server(self) -> str:
        """Returns MetaTrader server which hosts the account.

        Returns:
            MetaTrader server which hosts the account.
        """

    @property
    @abstractmethod
    def synchronization_mode(self):
        """Returns synchronization mode, can be automatic or user. See
        https://metaapi.cloud/docs/client/websocket/synchronizationMode/ for more details.

        Returns:
            Synchronization mode.
        """

    @property
    @abstractmethod
    def provisioning_profile_id(self):
        """Returns id of the account's provisioning profile.

        Returns:
            Id of the account's provisioning profile.
        """

    @property
    @abstractmethod
    def time_converter(self):
        """Returns algorithm used to parse your broker timezone. Supported values are icmarkets for
        America/New_York DST switch and roboforex for EET DST switch (the values will be changed soon)

        Returns:
            Algorithm used to parse your broker timezone.
        """

    @property
    @abstractmethod
    def application(self):
        """Returns application name to connect the account to. Currently allowed values are MetaApi and AgiliumTrade.

        Returns:
            Application name to connect the account to.
        """

    @property
    @abstractmethod
    def magic(self):
        """Returns MetaTrader magic to place trades using.

        Returns:
            MetaTrader magic to place trades using.
        """

    @property
    @abstractmethod
    def state(self):
        """Returns account deployment state. One of CREATED, DEPLOYING, DEPLOYED, UNDEPLOYING, UNDEPLOYED, DELETING

        Returns:
            Account deployment state.
        """

    @property
    @abstractmethod
    def connection_status(self):
        """Returns terminal & broker connection status, one of CONNECTED, DISCONNECTED, DISCONNECTED_FROM_BROKER

        Returns:
            Terminal & broker connection status.
        """

    @property
    @abstractmethod
    def access_token(self):
        """Returns authorization access token to be used for accessing single account data.
        Intended to be used in browser API.

        Returns:
            Authorization token.
        """

    @abstractmethod
    async def reload(self):
        """Reloads MetaTrader account from API.

        Returns:
            A coroutine resolving when MetaTrader account is updated.
        """

    @abstractmethod
    async def remove(self):
        """Removes MetaTrader account. Cloud account transitions to DELETING state.
        It takes some time for an account to be eventually deleted. Self-hosted account is deleted immediately.

        Returns:
            A coroutine resolving when account is scheduled for deletion.
        """

    @abstractmethod
    async def deploy(self):
        """Schedules account for deployment. It takes some time for API server to be started and account to reach the
        DEPLOYED state.

        Returns:
            A coroutine resolving when account is scheduled for deployment.
        """

    @abstractmethod
    async def undeploy(self):
        """Schedules account for undeployment. It takes some time for API server to be stopped and account to reach the
        UNDEPLOYED state.

        Returns:
            A coroutine resolving when account is scheduled for undeployment.
        """

    @abstractmethod
    async def redeploy(self):
        """Schedules account for redeployment. It takes some time for API server to be restarted and account to reach
        the DEPLOYED state.

        Returns:
            A coroutine resolving when account is scheduled for redeployment.
        """

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    async def wait_connected(self, timeout_in_seconds=300, interval_in_milliseconds=1000):
        """Waits until API server has connected to the terminal and terminal has connected to the broker.

        Args:
            timeout_in_seconds: Wait timeout in seconds, default is 5m.
            interval_in_milliseconds: Interval between account reloads while waiting for a change, default is 1s.

        Returns:
            A coroutine which resolves when API server is connected to the broker.

        Raises:
            TimeoutException: If account has not connected to the broker within timeout allowed.
        """

    @abstractmethod
    async def connect(self, history_storage: Optional[HistoryStorage]):
        """Connects to MetaApi.

        Args:
            history_storage: optional history storage

        Returns:
            MetaApi connection.
        """

    @abstractmethod
    async def _delay(self, timeout_in_milliseconds):
        pass
