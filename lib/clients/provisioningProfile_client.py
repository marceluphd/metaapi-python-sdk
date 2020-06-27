from typing_extensions import TypedDict
from .httpClient import HttpClient
from requests import Response


class ProvisioningProfileDto(TypedDict):
    """Provisioning profile model"""

    _id: str
    """Provisioning profile unique identifier"""
    name: str
    """Provisioning profile name"""
    version: int
    """MetaTrader version (allowed values are 4 and 5)"""
    status: str
    """Provisioning profile status (allowed values are new and active)"""


class NewProvisioningProfileDto(TypedDict):
    """New provisioning profile model."""

    name: str
    """Provisioning profile name."""
    version: int
    """MetaTrader version (allowed values are 4 and 5)."""


class ProvisioningProfileIdDto(TypedDict):
    """Provisioning profile id model."""

    id: str
    """Provisioning profile unique identifier."""


class ProvisioningProfileUpdateDto(TypedDict):
    """Updated provisioning profile data."""

    name: str
    """Provisioning profile name."""


class ProvisioningProfileClient:
    """metaapi.cloud provisioning profile API client (see https://metaapi.cloud/docs/provisioning/)"""

    def __init__(self, http_client: HttpClient, token: str, domain: str = 'agiliumtrade.agiliumtrade.ai'):
        """Inits provisioning API client instance

        Args:
            http_client: HTTP client.
            token: Authorization token.
            domain: Domain to connect to, default is agiliumtrade.agiliumtrade.ai.
        """
        super().__init__()
        self._httpClient = http_client
        self._host = f"https://mt-provisioning-api-v1.{domain}"
        self._token = token

    async def get_provisioning_profiles(self, version: int, status: str) -> Response:
        """Retrieves provisioning profiles owned by user
        (see https://metaapi.cloud/docs/provisioning/api/provisioningProfile/readProvisioningProfiles/)

        Args:
            version: Optional version filter (allowed values are 4 and 5).
            status: Optional status filter (allowed values are new and active).

        Returns:
            A coroutine resolving with provisioning profiles found
        """
        params = {}
        if version:
            params['version'] = version
        if status:
            params['status'] = status
        opts = {
            'url': f"{self._host}/users/current/provisioning-profiles",
            'method': 'GET',
            'params': params,
            'headers': {
                'auth-token': self._token
            }
        }
        return await self._httpClient.request(opts)

    async def get_provisioning_profile(self, id: str) -> Response:
        """Retrieves a provisioning profile by id (see
        https://metaapi.cloud/docs/provisioning/api/provisioningProfile/readProvisioningProfile/). Throws an error if
        profile is not found.

        Args:
            id: Provisioning profile id.

        Returns:
            A coroutine resolving with provisioning profile found.
        """
        opts = {
            'url': f"{self._host}/users/current/provisioning-profiles/{id}",
            'method': 'GET',
            'headers': {
                'auth-token': self._token
            }
        }
        return await self._httpClient.request(opts)

    async def create_provisioning_profile(self, provisioning_profile: NewProvisioningProfileDto) -> Response:
        """Creates a new provisioning profile (see
        https://metaapi.cloud/docs/provisioning/api/provisioningProfile/createNewProvisioningProfile/). After creating
        a provisioning profile you are required to upload extra files in order to activate the profile for further use.

        Args:
            provisioning_profile: Provisioning profile to create.

        Returns:
            A coroutine resolving with an id of the provisioning profile created.
        """
        opts = {
            'url': f"{self._host}/users/current/provisioning-profiles",
            'method': 'POST',
            'headers': {
                'auth-token': self._token
            },
            'body': provisioning_profile
        }
        return await self._httpClient.request(opts)

    async def upload_provisioning_profile_file(self, provisioning_profile_id: str,
                                               file_name: str, file: str or memoryview) -> Response:
        """Uploads a file to a provisioning profile (see
        https://metaapi.cloud/docs/provisioning/api/provisioningProfile/uploadFilesToProvisioningProfile/).

        Args:
            provisioning_profile_id: Provisioning profile id to upload file to.
            file_name: Name of the file to upload. Allowed values are servers.dat for MT5 profile, broker.srv for
            MT4 profile.
            file: Path to a file to upload or buffer containing file contents.

        Returns:
            A coroutine resolving when file upload is completed.
        """
        if type(file) == str:
            file = open(file, 'rb').read()
        opts = {
            'method': 'PUT',
            'url': f'{self._host}/users/current/provisioning-profiles/{provisioning_profile_id}/{file_name}',
            'files': {
                'file': file
            },
            'headers': {
                'auth-token': self._token
            }
        }
        return await self._httpClient.request(opts)

    async def delete_provisioning_profile(self, id: str) -> Response:
        """ Deletes a provisioning profile (see
        https://metaapi.cloud/docs/provisioning/api/provisioningProfile/deleteProvisioningProfile/).
        Please note that in order to delete a provisioning profile you need to delete MT accounts connected to it first.

        Args:
            id: Provisioning profile id.

        Returns:
            A coroutine resolving when provisioning profile is deleted.
        """
        opts = {
            'url': f'{self._host}/users/current/provisioning-profiles/{id}',
            'method': 'DELETE',
            'headers': {
                'auth-token': self._token
            }
        }
        return await self._httpClient.request(opts)

    async def update_provisioning_profile(self, id: str, provisioning_profile: ProvisioningProfileUpdateDto):
        """Updates existing provisioning profile data (see
        https://metaapi.cloud/docs/provisioning/api/provisioningProfile/updateProvisioningProfile/).

        Args:
            id: Provisioning profile id.
            provisioning_profile: Updated provisioning profile.

        Returns:
            A coroutine resolving when provisioning profile is updated.
        """
        opts = {
            'url': f'{self._host}/users/current/provisioning-profiles/{id}',
            'method': 'PUT',
            'headers': {
                'auth-token': self._token
            },
            'body': provisioning_profile
        }
        return await self._httpClient.request(opts)
