from ..clients.metaApi.metatraderDemoAccount_client import MetatraderDemoAccountClient, NewMT4DemoAccount, \
    NewMT5DemoAccount
from .metatraderDemoAccount import MetatraderDemoAccount


class MetatraderDemoAccountApi:
    """Exposes MetaTrader demo account API logic to the consumers."""

    def __init__(self, metatrader_demo_account_client: MetatraderDemoAccountClient):
        """Inits a MetaTrader demo account API instance.

        Args:
            metatrader_demo_account_client: MetaTrader demo account REST API client.
        """
        self._metatraderDemoAccountClient = metatrader_demo_account_client

    async def create_mt4_demo_account(self, profile_id: str, account: NewMT4DemoAccount):
        """Creates new MetaTrader 4 demo account.

        Args:
            profile_id: Id of the provisioning profile that will be used as the basis for creating this account.
            account: Demo account to create.
        """
        demo_account = await self._metatraderDemoAccountClient.create_mt4_demo_account(profile_id, account)
        return MetatraderDemoAccount(demo_account)

    async def create_mt5_demo_account(self, profile_id: str, account: NewMT5DemoAccount):
        """Creates new MetaTrader 5 demo account.

        Args:
            profile_id: Id of the provisioning profile that will be used as the basis for creating this account.
            account: Demo account to create.
        """
        demo_account = await self._metatraderDemoAccountClient.create_mt5_demo_account(profile_id, account)
        return MetatraderDemoAccount(demo_account)
