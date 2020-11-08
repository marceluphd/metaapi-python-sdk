from ..metaApi_client import MetaApiClient
from typing_extensions import TypedDict
from typing import Optional


class NewMT4DemoAccount(TypedDict):
    """New MetaTrader 4 demo account model."""
    accountType: Optional[str]
    """Account type."""
    address: Optional[str]
    """Account holder's address."""
    balance: float
    """Account balance."""
    city: Optional[str]
    """Account holder's city."""
    country: Optional[str]
    """Account holder's country."""
    email: str
    """Account holder's email."""
    leverage: float
    """Account leverage."""
    name: Optional[str]
    """Account holder's name."""
    phone: Optional[str]
    """Account holder's phone."""
    serverName: str
    """Server name."""
    state: Optional[str]
    """Account holder's state"""
    zip: Optional[str]
    """Zip address."""


class NewMT5DemoAccount(TypedDict):
    """New MetaTrader 5 demo account model."""
    address: Optional[str]
    """Account holder's address."""
    balance: float
    """Account balance."""
    city: Optional[str]
    """Account holder's city."""
    country: Optional[str]
    """Account holder's country."""
    email: str
    """Account holder's email."""
    languageId: Optional[int]
    """Language id (default is 1)"""
    leverage: float
    """Account leverage."""
    name: Optional[str]
    """Account holder's name."""
    phone: Optional[str]
    """Account holder's phone."""
    serverName: str
    """Server name."""
    state: Optional[str]
    """Account holder's state"""
    zip: Optional[str]
    """Zip address."""


class MetatraderDemoAccountDto(TypedDict):
    """MetaTrader demo account model."""
    login: str
    """Account login."""
    password: str
    """Account password."""
    serverName: str
    """MetaTrader server name."""
    investorPassword: str
    """Account investor (read-only) password."""


class MetatraderDemoAccountClient(MetaApiClient):
    """metaapi.cloud MetaTrader demo account API client."""

    async def create_mt4_demo_account(self, profile_id: str, account: NewMT4DemoAccount) -> MetatraderDemoAccountDto:
        """Creates new MetaTrader 4 demo account.
        Method is accessible only with API access token.

        Args:
            profile_id: Id of the provisioning profile that will be used as the basis for creating this account.
            account: Demo account to create.

        Returns:
            A coroutine resolving with MetaTrader demo account created.
        """
        if self._is_not_jwt_token():
            return self._handle_no_access_exception('create_mt4_demo_account')
        opts = {
            'url': f'{self._host}/users/current/provisioning-profiles/{profile_id}/mt4-demo-accounts',
            'method': 'POST',
            'headers': {
                'auth-token': self._token
            },
            'body': account
        }
        return await self._httpClient.request(opts)

    async def create_mt5_demo_account(self, profile_id: str, account: NewMT5DemoAccount) -> MetatraderDemoAccountDto:
        """Creates new MetaTrader 5 demo account.
        Method is accessible only with API access token.

        Args:
            profile_id: Id of the provisioning profile that will be used as the basis for creating this account.
            account: Demo account to create.

        Returns:
            A coroutine resolving with MetaTrader demo account created.
        """
        if self._is_not_jwt_token():
            return self._handle_no_access_exception('create_mt5_demo_account')
        opts = {
            'url': f'{self._host}/users/current/provisioning-profiles/{profile_id}/mt5-demo-accounts',
            'method': 'POST',
            'headers': {
                'auth-token': self._token
            },
            'body': account
        }
        return await self._httpClient.request(opts)
