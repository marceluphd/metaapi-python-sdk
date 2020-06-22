import os
from dotenv import load_dotenv
import asyncio
from lib import MetaApi
from datetime import datetime, timedelta
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

token = os.getenv('TOKEN') or '<put in your token here>'
login = os.getenv('LOGIN') or '<put in your MT login here>'
password = os.getenv('PASSWORD') or '<put in your MT password here>'
server_name = os.getenv('SERVER') or '<put in your MT server name here>'
server_dat_file = os.getenv('PATH_TO_SERVERS_DAT') or '/path/to/your/servers.dat'
api = MetaApi(token)


async def test_meta_api_synchronization():
    try:
        profiles = await api.provisioning_profile_api.get_provisioning_profiles()

        # create test MetaTrader account profile
        profile = None
        for item in profiles:
            if item.name == server_name:
               profile = item
        if not profile:
            print('Creating account profile')
            profile = await api.provisioning_profile_api.create_provisioning_profile({
                'name': server_name,
                'version': 5
            })
            await profile.upload_file('servers.dat', server_dat_file)
        if profile and profile.status == 'new':
            print('Uploading servers.dat')
            await profile.upload_file('servers.dat', server_dat_file)
        else:
            print('Account profile already created')

        # Add test MetaTrader account
        accounts = await api.metatrader_account_api.get_accounts()
        account = None
        for item in accounts:
            if item.login == login and item.synchronization_mode == 'automatic':
                account = item
                break
        if not account:
            print('Adding MT5 account to MetaApi')
            account = await api.metatrader_account_api.create_account({
                'name': 'Test account',
                'type': 'cloud',
                'login': login,
                'password': password,
                'server': server_name,
                'synchronizationMode': 'automatic',
                'provisioningProfileId': profile.id,
                'timeConverter': 'icmarkets',
                'application': 'MetaApi',
                'magic': 1000
            })
        else:
            print('MT5 account already added to MetaApi')

        #  wait until account is deployed and connected to broker
        print('Deploying account')
        await account.deploy()
        print('Waiting for API server to connect to broker (may take couple of minutes)')
        await account.wait_connected()

        # connect to MetaApi API
        connection = await account.connect()

        # wait until terminal state synchronized to the local state
        print('Waiting for SDK to synchronize to terminal state (may take some time depending on your history size)')
        await connection.wait_synchronized()

        # invoke RPC API (replace ticket numbers with actual ticket numbers which exist in your MT account)
        print('Testing MetaAPI RPC API')
        print('account information:', await connection.get_account_information())
        print('positions:', await connection.get_positions())
        # print(await connection.get_position('1234567'))
        print('open orders:', await connection.get_orders())
        # print(await connection.get_order('1234567'))
        print('history orders by ticket:', await connection.get_history_orders_by_ticket('1234567'))
        print('history orders by position:', await connection.get_history_orders_by_position('1234567'))
        print('history orders (~last 3 months):',
              await connection.get_history_orders_by_time_range(datetime.utcnow() - timedelta(days=90),
                                                                datetime.utcnow()))
        print('history deals by ticket:', await connection.get_deals_by_ticket('1234567'))
        print('history deals by position:', await connection.get_deals_by_position('1234567'))
        print('history deals (~last 3 months):',
              await connection.get_deals_by_time_range(datetime.utcnow() - timedelta(days=90), datetime.utcnow()))

        # trade
        print('Submitting pending order')
        result = await connection.create_limit_buy_order('GBPUSD', 0.07, 1.0, 0.9, 2.0, 'comment',
                                                         'TE_GBPUSD_7hyINWqAlE')
        if result['description'] == 'TRADE_RETCODE_DONE':
            print('Trade successful')
        else:
            print('Trade failed with ' + result['description'] + ' error')

        # finally, undeploy account after the test
        print('Undeploying MT5 account so that it does not consume any unwanted resources')
        await account.undeploy()
    except Exception as err:
        print(err)


async def main():
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(test_meta_api_synchronization(), loop=loop)
    await task

asyncio.run(main())

