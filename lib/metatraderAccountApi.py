from .metatraderAccount import MetatraderAccount
from .clients.metaApiWebsocket_client import MetaApiWebsocketClient
from .clients.metatraderAccount_client import MetatraderAccountClient
from .clients.metatraderAccount_client import NewMetatraderAccountDto
from typing import List


class MetatraderAccountApi:
    """Exposes MetaTrader account API logic to the consumers."""

    def __init__(self, metatrader_account_client: MetatraderAccountClient,
                 meta_api_websocket_client: MetaApiWebsocketClient):
        """Inits a MetaTrader account API instance.

        Args:
            metatrader_account_client: MetaTrader account REST API client.
            meta_api_websocket_client: MetaApi websocket client.
        """
        self._metatraderAccountClient = metatrader_account_client
        self._metaApiWebsocketClient = meta_api_websocket_client

    async def get_accounts(self, provisioning_profile_id: str = None) -> List[MetatraderAccount]:
        """Retrieves MetaTrader accounts.

        Args:
            provisioning_profile_id: Provisioning profile id.

        Returns:
            A coroutine resolving with an array of MetaTrader account entities.
        """
        accounts = await self._metatraderAccountClient.get_accounts(provisioning_profile_id)
        return list(map(lambda account: MetatraderAccount(account, self._metatraderAccountClient,
                                                          self._metaApiWebsocketClient), accounts))

    async def get_account(self, account_id) -> MetatraderAccount:
        """Retrieves a MetaTrader account by id.

        Args:
            account_id: MetaTrader account id.

        Returns:
            A coroutine resolving with MetaTrader account entity.
        """
        account = await self._metatraderAccountClient.get_account(account_id)
        return MetatraderAccount(account, self._metatraderAccountClient, self._metaApiWebsocketClient)

    async def create_account(self, account: NewMetatraderAccountDto) -> MetatraderAccount:
        """Creates a MetaTrader account.

        Args:
            account: MetaTrader account data.

        Returns:
            A coroutine resolving with MetaTrader account entity.
        """
        id = await self._metatraderAccountClient.create_account(account)
        return await self.get_account(id['id'])
