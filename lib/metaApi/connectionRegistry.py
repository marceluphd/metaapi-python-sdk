from .metaApiConnection import MetaApiConnection
from ..clients.metaApi.metaApiWebsocket_client import MetaApiWebsocketClient
from .metatraderAccountModel import MetatraderAccountModel
from .historyStorage import HistoryStorage
from .connectionRegistryModel import ConnectionRegistryModel
from datetime import datetime


class ConnectionRegistry(ConnectionRegistryModel):
    """Manages account connections"""

    def __init__(self, meta_api_websocket_client: MetaApiWebsocketClient, application: str = 'MetaApi'):
        """Inits a MetaTrader connection registry instance.

        Args:
            meta_api_websocket_client: MetaApi websocket client.
            application: Application type.
        """
        self._meta_api_websocket_client = meta_api_websocket_client
        self._application = application
        self._connections = {}

    async def connect(self, account: MetatraderAccountModel, history_storage: HistoryStorage,
                      history_start_time: datetime = None) -> MetaApiConnection:
        """Creates and returns a new account connection if doesnt exist, otherwise returns old.

        Args:
            account: MetaTrader account to connect to.
            history_storage: Terminal history storage.
            history_start_time: History start time.

        Returns:
            A coroutine resolving with account connection.
        """
        if account.id in self._connections:
            return self._connections[account.id]
        else:
            connection = MetaApiConnection(self._meta_api_websocket_client, account, history_storage, self,
                                           history_start_time)
            await connection.initialize()
            await connection.subscribe()
            self._connections[account.id] = connection
            return connection

    def remove(self, account_id: str):
        """Removes an account from registry.

        Args:
            account_id: MetaTrader account id to remove.
        """
        if account_id in self._connections:
            del self._connections[account_id]

    @property
    def application(self) -> str:
        """Returns application type.

        Returns:
            Application type.
        """
        return self._application
