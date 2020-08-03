import responses
import json
import mock as mock
import pytest
from .httpClient import HttpClient
from .provisioningProfile_client import ProvisioningProfileClient

PROVISIONING_API_URL = 'https://mt-provisioning-api-v1.agiliumtrade.agiliumtrade.ai'
httpClient = HttpClient()
provisioningClient = ProvisioningProfileClient(httpClient, 'token')


class TestProvisioningProfileClient:
    @pytest.mark.asyncio
    async def test_retrieve_many(self):
        """Should retrieve provisioning profiles from API."""
        expected = [{
            '_id': 'id',
            'name': 'name',
            'version': 4,
            'status': 'active'
        }]
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{PROVISIONING_API_URL}/users/current/provisioning-profiles',
                     json=expected, status=200)
            profiles = await provisioningClient.get_provisioning_profiles(5, 'active')
            assert rsps.calls[0].request.url == \
                f'{PROVISIONING_API_URL}/users/current/provisioning-profiles?version=5&status=active'
            assert rsps.calls[0].request.headers['auth-token'] == 'token'
            assert profiles == expected

    @pytest.mark.asyncio
    async def test_retrieve_one(self):
        """Should retrieve provisioning profile from API."""
        expected = {
            '_id': 'id',
            'name': 'name',
            'version': 4,
            'status': 'active'
        }
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, f'{PROVISIONING_API_URL}/users/current/provisioning-profiles/id',
                     json=expected, status=200)
            profile = await provisioningClient.get_provisioning_profile('id')
            assert rsps.calls[0].request.url == \
                f'{PROVISIONING_API_URL}/users/current/provisioning-profiles/id'
            assert rsps.calls[0].request.headers['auth-token'] == 'token'
            assert profile == expected

    @pytest.mark.asyncio
    async def test_create(self):
        """Should create provisioning profile via API."""
        expected = {
            'id': 'id'
        }
        profile = {
            'name': 'name',
            'version': 4,
        }
        with responses.RequestsMock() as rsps:
            rsps.add(responses.POST, f'{PROVISIONING_API_URL}/users/current/provisioning-profiles',
                     json=expected, status=200)
            id = await provisioningClient.create_provisioning_profile(profile)
            assert rsps.calls[0].request.url == f'{PROVISIONING_API_URL}/users/current/provisioning-profiles'
            assert rsps.calls[0].request.headers['auth-token'] == 'token'
            assert rsps.calls[0].request.body == json.dumps(profile).encode('utf-8')
            assert id == expected

    @pytest.mark.asyncio
    async def test_upload(self):
        """Should upload file to a provisioning profile via API."""
        with responses.RequestsMock() as rsps:
            rsps.add(responses.PUT, f'{PROVISIONING_API_URL}/users/current/provisioning-profiles/id/servers.dat',
                     status=204)
            with mock.patch('__main__.open', new=mock.mock_open(read_data='test')) as file:
                file.return_value = 'test', 'test2'
                await provisioningClient.upload_provisioning_profile_file('id', 'servers.dat', file())
                assert rsps.calls[0].request.url == \
                    f'{PROVISIONING_API_URL}/users/current/provisioning-profiles/id/servers.dat'
                assert rsps.calls[0].request.headers['auth-token'] == 'token'

    @pytest.mark.asyncio
    async def test_delete(self):
        """Should delete provisioning profile via API."""
        with responses.RequestsMock() as rsps:
            rsps.add(responses.DELETE, f'{PROVISIONING_API_URL}/users/current/provisioning-profiles/id',
                     status=204)
            await provisioningClient.delete_provisioning_profile('id')
            assert rsps.calls[0].request.url == \
                f'{PROVISIONING_API_URL}/users/current/provisioning-profiles/id'
            assert rsps.calls[0].request.headers['auth-token'] == 'token'

    @pytest.mark.asyncio
    async def test_update(self):
        """Should update provisioning profile via API."""
        with responses.RequestsMock() as rsps:
            rsps.add(responses.PUT, f'{PROVISIONING_API_URL}/users/current/provisioning-profiles/id',
                     status=204)
            await provisioningClient.update_provisioning_profile('id', {'name': 'new name'})
            assert rsps.calls[0].request.url == \
                   f'{PROVISIONING_API_URL}/users/current/provisioning-profiles/id'
            assert rsps.calls[0].request.headers['auth-token'] == 'token'
            assert rsps.calls[0].request.body == json.dumps({'name': 'new name'}).encode('utf-8')
