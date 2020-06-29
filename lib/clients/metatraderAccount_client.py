from .httpClient import HttpClient
from typing_extensions import TypedDict
from requests import Response


class MetatraderAccountIdDto(TypedDict):
    """MetaTrader account id model"""

    id: str
    """MetaTrader account unique identifier"""


class MetatraderAccountDto(TypedDict):
    """MetaTrader account model"""

    _id: str
    """Account unique identifier."""
    name: str
    """MetaTrader account human-readable name in the MetaApi app."""
    type: str
    """Account type, can be cloud or self-hosted."""
    login: str
    """MetaTrader account number."""
    server: str
    """MetaTrader server which hosts the account."""
    synchronizationMode: str
    """Synchronization mode, can be automatic or user. See
    https://metaapi.cloud/docs/client/websocket/synchronizationMode/ for more details."""
    provisioningProfileId: str
    """Id of the account's provisioning profile."""
    timeConverter: str
    """Algorithm used to parse your broker timezone. Supported values are icmarkets for America/New_York DST switch
    and roboforex for EET DST switch (the values will be changed soon)"""
    application: str
    """Application name to connect the account to. Currently allowed values are MetaApi and AgiliumTrade"""
    magic: int
    """MetaTrader magic to place trades using."""
    state: str
    """Account deployment state. One of CREATED, DEPLOYING, DEPLOYED, UNDEPLOYING, UNDEPLOYED, DELETING"""
    connectionStatus: str
    """Terminal & broker connection status, one of CONNECTED, DISCONNECTED, DISCONNECTED_FROM_BROKER"""
    accessToken: str
    """Authorization token to be used for accessing single account data. Intended to be used in browser API."""


class NewMetatraderAccountDto(TypedDict):
    """New MetaTrader account model"""

    name: str
    """MetaTrader account human-readable name in the MetaApi app."""
    type: str
    """Account type, can be cloud or self-hosted."""
    login: str
    """MetaTrader account number."""
    password: str
    """MetaTrader account password. The password can be either investor password for read-only access or master
    password to enable trading features. Required for cloud account."""
    server: str
    """MetaTrader server which hosts the account."""
    synchronizationMode: str
    """Synchronization mode, can be automatic or user. See
    https://metaapi.cloud/docs/client/websocket/synchronizationMode/ for more details."""
    provisioningProfileId: str
    """Id of the account's provisioning profile."""
    timeConverter: str
    """Algorithm used to parse your broker timezone. Supported values are icmarkets for America/New_York DST switch
    and roboforex for EET DST switch (the values will be changed soon)."""
    application: str
    """Application name to connect the account to. Currently allowed values are MetaApi and AgiliumTrade."""
    magic: int
    """MetaTrader magic to place trades using."""


class MetatraderAccountUpdateDto(TypedDict):
    """Updated MetaTrader account data"""

    name: str
    """MetaTrader account human-readable name in the MetaApi app."""
    password: str
    """MetaTrader account password. The password can be either investor password for read-only
    access or master password to enable trading features. Required for cloud account"""
    server: str
    """MetaTrader server which hosts the account"""
    synchronizationMode: str
    """Synchronization mode, can be automatic or user. See
    https://metaapi.cloud/docs/client/websocket/synchronizationMode/ for more details."""


class MetatraderAccountClient:
    """metaapi.cloud MetaTrader account API client (see https://metaapi.cloud/docs/provisioning/)

    Attributes:
        _httpClient: HTTP client
        _host: domain to connect to
        _token: authorization token
    """

    def __init__(self, http_client: HttpClient, token: str, domain: str = 'agiliumtrade.agiliumtrade.ai'):
        """Inits MetaTrader account API client instance.

        Args:
            http_client: HTTP client.
            token: Authorization token.
            domain: Domain to connect to, default is agiliumtrade.agiliumtrade.ai.
        """
        self._httpClient = http_client
        self._host = f'https://mt-provisioning-api-v1.{domain}'
        self._token = token

    async def get_accounts(self, provisioning_profile_id: str = None) -> Response:
        """Retrieves MetaTrader accounts owned by user
        (see https://metaapi.cloud/docs/provisioning/api/account/readAccounts/)

        Args:
            provisioning_profile_id: Optional provisioning profile id filter.

        Returns:
            A coroutine resolving with List[MetatraderAccountDto] - MetaTrader accounts found.
        """
        params = {}
        if provisioning_profile_id:
            params['provisioningProfileId'] = provisioning_profile_id
        opts = {
            'url': f'{self._host}/users/current/accounts',
            'method': 'GET',
            'params': params,
            'headers': {
                'auth-token': self._token
            }
        }
        return await self._httpClient.request(opts)

    async def get_account(self, id: str) -> Response:
        """Retrieves a MetaTrader account by id (see https://metaapi.cloud/docs/provisioning/api/account/readAccount/).
        Throws an error if account is not found.

        Args:
            id: MetaTrader account id.

        Returns:
            A coroutine resolving with MetatraderAccountDto - MetaTrader account found.
        """
        opts = {
            'url': f'{self._host}/users/current/accounts/{id}',
            'method': 'GET',
            'headers': {
                'auth-token': self._token
            }
        }
        return await self._httpClient.request(opts)

    async def create_account(self, account: NewMetatraderAccountDto) -> Response:
        """Starts cloud API server for a MetaTrader account using specified provisioning profile
        (see https://metaapi.cloud/docs/provisioning/api/account/createAccount/).
        It takes some time to launch the terminal and connect the terminal to the broker, you can use the
        connectionStatus field to monitor the current status of the terminal.

        Args:
            account: MetaTrader account to create.

        Returns:
            A coroutine resolving with MetatraderAccountIdDto - an id of the MetaTrader account created.
        """
        opts = {
            'url': f'{self._host}/users/current/accounts',
            'method': 'POST',
            'headers': {
                'auth-token': self._token
            },
            'body': account
        }
        return await self._httpClient.request(opts)

    async def deploy_account(self, id: str) -> Response:
        """Starts API server for MetaTrader account. This request will be ignored if the account has already
        been deployed. (see https://metaapi.cloud/docs/provisioning/api/account/deployAccount/)

        Args:
            id: MetaTrader account id to deploy.

        Returns:
            A coroutine resolving when MetaTrader account is scheduled for deployment
        """
        opts = {
            'url': f'{self._host}/users/current/accounts/{id}/deploy',
            'method': 'POST',
            'headers': {
                'auth-token': self._token
            }
        }
        return await self._httpClient.request(opts)

    async def undeploy_account(self, id: str) -> Response:
        """Stops API server for a MetaTrader account. Terminal data such as downloaded market history data will
        be preserved. (see https://metaapi.cloud/docs/provisioning/api/account/undeployAccount/)

        Args:
            id: MetaTrader account id to undeploy.

        Returns:
            A coroutine resolving when MetaTrader account is scheduled for undeployment.
        """
        opts = {
            'url': f'{self._host}/users/current/accounts/{id}/undeploy',
            'method': 'POST',
            'headers': {
                'auth-token': self._token
            }
        }
        return await self._httpClient.request(opts)

    async def redeploy_account(self, id: str) -> Response:
        """Redeploys MetaTrader account. This is equivalent to undeploy immediately followed by deploy.
        (see https://metaapi.cloud/docs/provisioning/api/account/redeployAccount/)

        Args:
            id: MetaTrader account id to redeploy.

        Returns:
            A coroutine resolving when MetaTrader account is scheduled for redeployment.
        """
        opts = {
            'url': f'{self._host}/users/current/accounts/{id}/redeploy',
            'method': 'POST',
            'headers': {
                'auth-token': self._token
            }
        }
        return await self._httpClient.request(opts)

    async def delete_account(self, id: str) -> Response:
        """Stops and deletes an API server for a specified MetaTrader account. The terminal state such as downloaded
        market data history will be deleted as well when you delete the account.
        (see https://metaapi.cloud/docs/provisioning/api/account/deleteAccount/)

        Args:
            id: MetaTrader account id to delete.

        Returns:
            A coroutine resolving when MetaTrader account is scheduled for deletion.
        """
        opts = {
            'url': f'{self._host}/users/current/accounts/{id}',
            'method': 'DELETE',
            'headers': {
                'auth-token': self._token
            }
        }
        return await self._httpClient.request(opts)

    async def update_account(self, id: str, account: MetatraderAccountUpdateDto) -> Response:
        """Updates existing metatrader account data (see
        https://metaapi.cloud/docs/provisioning/api/account/updateAccount/)

        Args:
            id: MetaTrader account id.
            account: Updated MetaTrader account.

        Returns:
            A coroutine resolving when MetaTrader account is updated.
        """
        opts = {
            'url': f'{self._host}/users/current/accounts/{id}',
            'method': 'PUT',
            'headers': {
                'auth-token': self._token
            },
            'body': account
        }
        return await self._httpClient.request(opts)
