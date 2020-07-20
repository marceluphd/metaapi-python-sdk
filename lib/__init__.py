from .clients.httpClient import HttpClient
from .clients.metaApiWebsocket_client import MetaApiWebsocketClient
from .provisioningProfileApi import ProvisioningProfileApi
from .clients.provisioningProfile_client import ProvisioningProfileClient
from .metatraderAccountApi import MetatraderAccountApi
from .clients.metatraderAccount_client import MetatraderAccountClient
from .historyStorage import HistoryStorage
from .memoryHistoryStorage import MemoryHistoryStorage
from .clients.synchronizationListener import SynchronizationListener


class MetaApi:
    """MetaApi MetaTrader API SDK"""

    def __init__(self, token: str, domain: str = 'agiliumtrade.agiliumtrade.ai', request_timeout: float = 60,
                 connect_timeout: float = 60):
        """Inits MetaApi class instance.

        Args:
            token: Authorization token.
            domain: Domain to connect to.
        """
        http_client = HttpClient(request_timeout)
        self._metaApiWebsocketClient = MetaApiWebsocketClient(token, domain, request_timeout, connect_timeout)
        self._provisioningProfileApi = ProvisioningProfileApi(ProvisioningProfileClient(http_client, token, domain))
        self._metatraderAccountApi = MetatraderAccountApi(MetatraderAccountClient(http_client, token, domain),
                                                          self._metaApiWebsocketClient)

    @property
    def provisioning_profile_api(self) -> ProvisioningProfileApi:
        """Returns provisioning profile API.

        Returns:
            Provisioning profile API.
        """
        return self._provisioningProfileApi

    @property
    def metatrader_account_api(self) -> MetatraderAccountApi:
        """Returns MetaTrader account API.

        Returns:
            MetaTrader account API.
        """
        return self._metatraderAccountApi

    def close(self):
        """Closes all clients and connections"""
        self._metaApiWebsocketClient.close()
