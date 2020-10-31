from ..clients.httpClient import HttpClient
from ..clients.metaApi.metaApiWebsocket_client import MetaApiWebsocketClient
from ..metaApi.provisioningProfileApi import ProvisioningProfileApi
from ..clients.metaApi.provisioningProfile_client import ProvisioningProfileClient
from ..metaApi.metatraderAccountApi import MetatraderAccountApi
from ..clients.metaApi.metatraderAccount_client import MetatraderAccountClient
from ..clients.errorHandler import ValidationException
from ..metaApi.connectionRegistry import ConnectionRegistry
import re


class MetaApi:
    """MetaApi MetaTrader API SDK"""

    def __init__(self, token: str, application: str = 'MetaApi', domain: str = 'agiliumtrade.agiliumtrade.ai',
                 request_timeout: float = 60, connect_timeout: float = 60):
        """Inits MetaApi class instance.

        Args:
            token: Authorization token.
            application: Application id.
            domain: Domain to connect to.
            request_timeout: Timeout for http requests in seconds.
            connect_timeout: Timeout for connecting to server in seconds.
        """
        if not re.search(r"[a-zA-Z0-9_]+", application):
            raise ValidationException('Application name must be non-empty string consisting ' +
                                      'from letters, digits and _ only')
        http_client = HttpClient(request_timeout)
        self._metaApiWebsocketClient = MetaApiWebsocketClient(token, application, domain, request_timeout,
                                                              connect_timeout)
        self._provisioningProfileApi = ProvisioningProfileApi(ProvisioningProfileClient(http_client, token, domain))
        self._connectionRegistry = ConnectionRegistry(self._metaApiWebsocketClient, application)
        self._metatraderAccountApi = MetatraderAccountApi(MetatraderAccountClient(http_client, token, domain),
                                                          self._metaApiWebsocketClient, self._connectionRegistry)

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
