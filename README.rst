metaapi.cloud SDK for Python
============================

MetaApi is a powerful API for MetaTrader 4 and MetaTrader 5 terminals.
MetaApi is available in cloud and self-hosted options.

Official REST and websocket API documentation: https://metaapi.cloud/docs/client/

Please note that this SDK provides an abstraction over REST and websocket API to simplify your application logic.
For more information about SDK APIs please check docstring documentation in source codes located inside lib folder of this package.

Installation
------------
.. code-block:: bash

    pip install metaapi-cloud-sdk

Obtaining MetaApi token
-----------------------
You can obtain MetaApi token via https://app.metaapi.cloud/token UI.

Working code examples
---------------------
You can find code examples at `examples folder of our github repo <https://github.com/agiliumtrade-ai/metaapi-python-client/tree/master/examples>`_ or in the examples folder of the pip package.

Add MetaTrader account to MetaApi
---------------------------------
You can use https://app.metaapi.cloud/accounts UI to add a MetaTrader
account to MetaApi application. Alternatively you can use API as
demonstrated below.

Add MetaTrader account to MetaApi via API
-----------------------------------------

.. code-block:: python

    from metaapi_cloud_sdk import MetaApi

    token = '...'
    api = MetaApi(token)

    # if you do not have created a provisioning profile for your broker,
    # you should do it before creating an account
    provisioningProfile = await api.provisioning_profile_api.create_provisioning_profile({
        'name': 'My profile',
        'version': 5
    })
    # servers.dat file is required for MT5 profile and can be found inside
    # config directory of your MetaTrader terminal data folder. It contains
    # information about available broker servers
    await provisioningProfile.upload_file('servers.dat', '/path/to/servers.dat')
    # for MT4, you should upload an .srv file instead
    # await provisioningProfile.upload_file('broker.srv', '/path/to/broker.srv');

    # Alternatively you can retrieve an existing profile from API
    # provisioningProfile = await api.provisioning_profile_api.get_provisioning_profile('profileId');

    # if you have not yet added your MetaTrader account, then add it
    account = await api.metatrader_account_api.create_account({
      'name': 'Trading account #1',
      'type': 'cloud',
      'login': '1234567',
      # password can be investor password for read-only access
      'password': 'qwerty',
      'server': 'ICMarketsSC-Demo',
      # synchronizationMode can be 'automatic' for RPC access or 'user' if you
      # want to keep track of terminal state in real-time (e.g. if you are
      # developing a EA or trading strategy)
      'synchronizationMode': 'automatic',
      'provisioningProfileId': provisioningProfile.id,
      # algorithm used to parse your broker timezone. Supported values are
      # icmarkets for America/New_York DST switch and roboforex for EET
      # DST switch (the values will be changed soon)
      'timeConverter': 'roboforex',
      'application': 'MetaApi',
      'magic': 123456
    })

    # Alternatively you can retrieve an existing account from API
    # account = await api.metatrader_account_api.get_account('accountId');

Access MetaTrader account via RPC API
-------------------------------------
RPC API let you query the trading terminal state. You should use
automatic synchronization mode if all you need is the RPC API.

.. code-block:: python

    from metaapi_cloud_sdk import MetaApi

    token = '...'
    api = MetaApi(token)

    account = await api.metatrader_account_api.get_account('accountId')

    connection = await account.connect()

    await connection.wait_synchronized()

    # retrieve balance and equity
    print(await connection.get_account_information())
    # retrieve open positions
    print(await connection.get_positions())
    # retrieve a position by id
    print(await connection.get_position('1234567'))
    # retrieve pending orders
    print(await connection.get_orders())
    # retrieve a pending order by id
    print(await connection.get_order('1234567'))
    # retrieve history orders by ticket
    print(await connection.get_history_orders_by_ticket('1234567'))
    # retrieve history orders by position id
    print(await connection.get_history_orders_by_position('1234567'))
    # retrieve history orders by time range
    print(await connection.get_history_orders_by_time_range(start_time, end_time))
    # retrieve history deals by ticket
    print(await connection.get_deals_by_ticket('1234567'))
    # retrieve history deals by position id
    print(await connection.get_deals_by_position('1234567'))
    # retrieve history deals by time range
    print(await connection.get_deals_by_time_range(start_time, end_time))

    # trade
    print(await connection.create_market_buy_order('GBPUSD', 0.07, 0.9, 2.0, 'comment', 'TE_GBPUSD_7hyINWqAlE'))
    print(await connection.create_market_sell_order('GBPUSD', 0.07, 2.0, 0.9, 'comment', 'TE_GBPUSD_7hyINWqAlE'))
    print(await connection.create_limit_buy_order('GBPUSD', 0.07, 1.0, 0.9, 2.0, 'comment', 'TE_GBPUSD_7hyINWqAlE'))
    print(await connection.create_limit_sell_order('GBPUSD', 0.07, 1.5, 2.0, 0.9, 'comment', 'TE_GBPUSD_7hyINWqAlE'))
    print(await connection.create_stop_buy_order('GBPUSD', 0.07, 1.5, 0.9, 2.0, 'comment', 'TE_GBPUSD_7hyINWqAlE'))
    print(await connection.create_stop_sell_order('GBPUSD', 0.07, 1.0, 2.0, 0.9, 'comment', 'TE_GBPUSD_7hyINWqAlE'))
    print(await connection.modify_position('46870472', 2.0, 0.9))
    print(await connection.close_position_partially('46870472', 0.9))
    print(await connection.close_position('46870472'))
    # this trade type is available for MT5 netting accounts only
    print(await connection.close_position_by_symbol('EURUSD'))
    print(await connection.modify_order('46870472', 0.07, 1.0, 2.0, 0.9))
    print(await connection.cancel_order('46870472'))

    # Note: trade methods do not throw an exception if terminal have refused
    # the trade, thus you must check the returned value
    result = await connection.create_market_buy_order('GBPUSD', 0.07, 0.9, 2.0, 'comment', 'TE_GBPUSD_7hyINWqAlE')
    if result['description'] != 'TRADE_RETCODE_DONE':
      print('Trade was rejected by MetaTrader terminal with ' + result['description'] + ' error')


    # you can release all MetaApi resource when you are done using it
    api.close()

Synchronize with MetaTrader terminal state in real-time
-------------------------------------------------------
If you are developing applications like trading strategy or an EA then
you'll likely need a real-time view of the terminal state. If this is
the case, then you should set your account synchronization mode to
'user' and use API below to access terminal state.

.. code-block:: python

    from metaapi_cloud_sdk import MetaApi, HistoryStorage, SynchronizationListener

    token = '...'
    api = MetaApi(token)

    account = await api.metatrader_account_api.get_account('accountId')

    # account.synchronization_mode must be equal to 'user' at this point

    class MongodbHistoryStorage(HistoryStorage):
      # implement the abstract methods, see MemoryHistoryStorage for sample
      # implementation

    historyStorage = MongodbHistoryStorage()

    # Note: if you will not specify history storage, then in-memory storage
    # will be used (instance of MemoryHistoryStorage)
    connection = await account.connect(historyStorage)

    # access local copy of terminal state
    terminalState = connection.terminal_state

    # wait until synchronization completed
    await connection.wait_synchronized()

    print(terminalState.connected)
    print(terminalState.connected_to_broker)
    print(terminalState.account_information)
    print(terminalState.positions)
    print(terminalState.orders)
    # symbol specifications
    print(terminalState.specifications)
    print(terminalState.specification('EURUSD'))
    print(terminalState.price('EURUSD'))

    # access history storage
    historyStorage = connection.history_storage

    # both orderSynchronizationFinished and dealSynchronizationFinished
    # should be true once history synchronization have finished
    print(historyStorage.order_synchronization_finished)
    print(historyStorage.deal_synchronization_finished)
    # invoke other methods provided by your history storage
    print(await historyStorage.your_method())

    # receive synchronization event notifications
    # first, implement your listener
    class MySynchronizationListener(SynchronizationListener):
      # override abstract methods you want to receive notifications for

    # now add the listener
    listener = MySynchronizationListener()
    connection.add_synchronization_listener(listener)
    # remove the listener when no longer needed
    connection.remove_synchronization_listener(listener)

    # close the connection to clean up resources
    connection.close()

    # you can release all MetaApi resource when you done using it
    api.close()


Keywords: MetaTrader API, MetaTrader REST API, MetaTrader websocket API,
MetaTrader 5 API, MetaTrader 5 REST API, MetaTrader 5 websocket API,
MetaTrader 4 API, MetaTrader 4 REST API, MetaTrader 4 websocket API,
MT5 API, MT5 REST API, MT5 websocket API, MT4 API, MT4 REST API,
MT4 websocket API, MetaTrader SDK, MetaTrader SDK, MT4 SDK, MT5 SDK,
MetaTrader 5 SDK, MetaTrader 4 SDK, MetaTrader python SDK, MetaTrader 5
python SDK, MetaTrader 4 python SDK, MT5 python SDK, MT4 python SDK,
FX REST API, Forex REST API, Forex websocket API, FX websocket API, FX
SDK, Forex SDK, FX python SDK, Forex python SDK, Trading API, Forex
API, FX API, Trading SDK, Trading REST API, Trading websocket API,
Trading SDK, Trading python SDK
