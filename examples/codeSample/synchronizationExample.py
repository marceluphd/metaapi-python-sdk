import os
import asyncio
from metaapi_cloud_sdk import MetaApi
from metaapi_cloud_sdk.clients.tradeException import TradeException

# Note: for information on how to use this example code please read https://metaapi.cloud/docs/client/usingCodeExamples

token = os.getenv('TOKEN') or '<put in your token here>'
accountId = os.getenv('ACCOUNT_ID') or '<put in your account id here>'
api = MetaApi(token)

async def test_meta_api_synchronization():
    try:
        account = await api.metatrader_account_api.get_account(accountId)

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

        # access local copy of terminal state
        print('Testing terminal state access')
        terminal_state = connection.terminal_state
        print('connected:', terminal_state.connected)
        print('connected to broker:', terminal_state.connected_to_broker)
        print('account information:', terminal_state.account_information)
        print('positions:', terminal_state.positions)
        print('orders:', terminal_state.orders)
        print('specifications:', terminal_state.specifications)
        print('EURUSD specification:', terminal_state.specification('EURUSD'))
        print('EURUSD price:', terminal_state.price('EURUSD'))

        # trade
        print('Submitting pending order')
        try:
            result = await connection.create_limit_buy_order('GBPUSD', 0.07, 1.0, 0.9, 2.0,
                                                             {'comment': 'comm', 'clientId': 'TE_GBPUSD_7hyINWqAlE'})
            print('Trade successful, result code is ' + result['stringCode'])
        except TradeException as err:
            print('Trade failed with result code ' + err.stringCode)

        # finally, undeploy account after the test
        print('Undeploying MT5 account so that it does not consume any unwanted resources')
        await account.undeploy()

    except Exception as err:
        print(err)

asyncio.run(test_meta_api_synchronization())
