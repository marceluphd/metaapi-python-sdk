from lib.clients.httpClient import HttpClient
from lib.clients.metaApiWebsocket_client import MetaApiWebsocketClient
from lib.provisioningProfileApi import ProvisioningProfileApi
from lib.clients.provisioningProfile_client import ProvisioningProfileClient
from lib.metatraderAccountApi import MetatraderAccountApi
from lib.clients.metatraderAccount_client import MetatraderAccountClient
from lib.historyStorage import HistoryStorage
from lib.memoryHistoryStorage import MemoryHistoryStorage
from lib.clients.synchronizationListener import SynchronizationListener


class MetaApi:
    """MetaApi MetaTrader API SDK"""

    def __init__(self, token: str, domain: str = 'agiliumtrade.agiliumtrade.ai'):
        """Constructs MetaApi class instance.

        Args:
            token: Authorization token.
            domain: Domain to connect to.
        """
        http_client = HttpClient()
        self._metaApiWebsocketClient = MetaApiWebsocketClient(token, domain)
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
