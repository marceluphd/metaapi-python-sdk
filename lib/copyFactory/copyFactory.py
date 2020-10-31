from ..clients.httpClient import HttpClient
from ..clients.copyFactory.configuration_client import ConfigurationClient
from ..clients.copyFactory.history_client import HistoryClient
from ..clients.copyFactory.trading_client import TradingClient


class CopyFactory:
    """MetaApi CopyFactory copy trading API SDK"""

    def __init__(self, token: str, domain: str = 'agiliumtrade.agiliumtrade.ai', request_timeout: float = 60):
        """Inits CopyFactory class instance.

        Args:
            token: Authorization token.
            domain: Domain to connect to.
            request_timeout: Timeout for http requests in seconds.
        """
        http_client = HttpClient(request_timeout)
        self._configurationClient = ConfigurationClient(http_client, token, domain)
        self._historyClient = HistoryClient(http_client, token, domain)
        self._tradingClient = TradingClient(http_client, token, domain)

    @property
    def configuration_api(self) -> ConfigurationClient:
        """Returns CopyFactory configuration API.

        Returns:
            Configuration API.
        """
        return self._configurationClient

    @property
    def history_api(self) -> HistoryClient:
        """Returns CopyFactory history API.

        Returns:
            History API.
        """
        return self._historyClient

    @property
    def trading_api(self) -> TradingClient:
        """Returns CopyFactory history API.

        Returns:
            History API.
        """
        return self._tradingClient
