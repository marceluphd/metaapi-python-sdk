import os
import asyncio
from metaapi_cloud_sdk import MetaApi
from metaapi_cloud_sdk.clients.synchronizationListener import SynchronizationListener
from metaapi_cloud_sdk.models import MetatraderSymbolPrice

token = os.getenv('TOKEN') or '<put in your token here>'
account_id = os.getenv('ACCOUNT_ID') or '<put in your account id here>'

api = MetaApi(token)

class EURUSDListener(SynchronizationListener):
    async def on_symbol_price_updated(self, price: MetatraderSymbolPrice):
        if price['symbol'] == 'EURUSD':
            print('EURUSD price updated', price)

async def stream_quotes():
    try:
        account = await api.metatrader_account_api.get_account(account_id)

        #  wait until account is deployed and connected to broker
        print('Deploying account')
        await account.deploy()
        print('Waiting for API server to connect to broker (may take couple of minutes)')
        await account.wait_connected()

        # connect to MetaApi API
        connection = await account.connect()

        eur_usd_listener = EURUSDListener()
        connection.add_synchronization_listener(eur_usd_listener)

        # wait until terminal state synchronized to the local state
        print('Waiting for SDK to synchronize to terminal state (may take some time depending on your history size), the price streaming will start once synchronization finishes')
        await connection.wait_synchronized(None, 1200)

        # Add symbol to MarketWatch if not yet added
        await connection.subscribe_to_market_data('EURUSD')

        print('Streaming EURUSD price now...');

        while True:
            await asyncio.sleep(1)

    except Exception as err:
        print(err)

asyncio.run(stream_quotes())
