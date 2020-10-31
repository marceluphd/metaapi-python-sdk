from ..metaApi_client import MetaApiClient
from .copyFactory_models import CopyFactoryStrategyStopout
from typing import List
from requests import Response


class TradingClient(MetaApiClient):
    """metaapi.cloud CopyFactory history API (trade copying history API) client (see
    https://trading-api-v1.project-stock.agiliumlabs.cloud/swagger/#/)"""

    def __init__(self, http_client, token: str, domain: str = 'agiliumtrade.agiliumtrade.ai'):
        """Inits CopyFactory history API client instance.

        Args:
            http_client: HTTP client.
            token: Authorization token.
            domain: Domain to connect to, default is agiliumtrade.agiliumtrade.ai.
        """
        super().__init__(http_client, token, domain)
        self._host = f'https://trading-api-v1.{domain}'

    async def resynchronize(self, account_id: str, strategy_ids: List[str]) -> Response:
        """Resynchronizes the account. See
        https://trading-api-v1.agiliumtrade.agiliumtrade.ai/swagger/#!/default
        /post_users_current_accounts_accountId_resynchronize

        Args:
            account_id: Account id.
            strategy_ids: Optional array of strategy ids to recynchronize. Default is to synchronize all strategies.

        Returns:
            A coroutine which resolves when resynchronization is scheduled.
        """
        if self._is_not_jwt_token():
            return self._handle_no_access_exception('resynchronize')
        opts = {
          'url': f'{self._host}/users/current/accounts/{account_id}/resynchronize',
          'method': 'POST',
          'headers': {
            'auth-token': self._token
          },
          'params': {
            'strategyId': strategy_ids
          },
        }
        return await self._httpClient.request(opts)

    async def get_stopouts(self, account_id: str) -> 'Response[List[CopyFactoryStrategyStopout]]':
        """Returns subscriber account stopouts. See
        https://trading-api-v1.agiliumtrade.agiliumtrade.ai/swagger/#!/default
        /get_users_current_accounts_accountId_stopouts

        Args:
            account_id: Account id.

        Returns:
            A coroutine which resolves with stopouts found.
        """
        if self._is_not_jwt_token():
            return self._handle_no_access_exception('get_stopouts')
        opts = {
            'url': f'{self._host}/users/current/accounts/{account_id}/stopouts',
            'method': 'GET',
            'headers': {
                'auth-token': self._token
            }
        }
        return await self._httpClient.request(opts)

    async def reset_stopout(self, account_id: str, reason: str) -> Response:
        """Resets account stopout. See
        https://trading-api-v1.agiliumtrade.agiliumtrade.ai/swagger/#!/default
        /post_users_current_accounts_accountId_stopouts_reason_reset

        Args:
            account_id: Account id.
            reason: Stopout reason to reset. One of yearly-balance, monthly-balance, daily-balance, yearly-equity,
            monthly-equity, daily-equity, max-drawdown.

        Returns:
            A coroutine which resolves when the stopout is reset.
        """
        if self._is_not_jwt_token():
            return self._handle_no_access_exception('reset_stopout')
        opts = {
            'url': f'{self._host}/users/current/accounts/{account_id}/stopouts/{reason}/reset',
            'method': 'POST',
            'headers': {
                'auth-token': self._token
            }
        }
        return await self._httpClient.request(opts)
