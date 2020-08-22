metaapi.cloud SDK for Python
############################

MetaApi is a powerful, fast, cost-efficient, easy to use and standards-driven cloud forex trading API for MetaTrader 4 and MetaTrader 5 platform designed for traders, investors and forex application developers to boost forex application development process. MetaApi can be used with any broker and does not require you to be a brokerage.

MetaApi is a paid service, but API access to one MetaTrader account is free of charge.

The `MetaApi pricing <https://metaapi.cloud/#pricing>`_ was developed with the intent to make your charges less or equal to what you would have to pay
for hosting your own infrastructure. This is possible because over time we managed to heavily optimize
our MetaTrader infrastructure. And with MetaApi you can save significantly on application development and
maintenance costs and time thanks to high-quality API, open-source SDKs and convenience of a cloud service.

Official REST and websocket API documentation: https://metaapi.cloud/docs/client/

Please note that this SDK provides an abstraction over REST and websocket API to simplify your application logic.

For more information about SDK APIs please check docstring documentation in source codes located inside lib folder of this package.

Installation
============
.. code-block:: bash

    pip install metaapi-cloud-sdk

Working code examples
=====================
Please check `this short video <https://youtu.be/LIqFOOOLP-g>`_ to see how you can download samples via our web application.

You can find code examples at `examples folder of our github repo <https://github.com/agiliumtrade-ai/metaapi-python-sdk/tree/master/examples>`_ or in the examples folder of the pip package.

We have composed a `short guide explaining how to use the example code <https://metaapi.cloud/docs/client/usingCodeExamples>`_

Connecting to MetaApi
=====================
Please use one of these ways:

1. https://app.metaapi.cloud/token web UI to obtain your API token.
2. An account access token which grants access to a single account. See section below on instructions on how to retrieve account access token.

Supply token to the MetaApi class constructor.

.. code-block:: python

    from metaapi_cloud_sdk import MetaApi

    token = '...'
    api = MetaApi(token)

Retrieving account access token
===============================
Account access token grants access to a single account. You can retrieve account access token via API:

.. code-block:: python

    account_id = '...'
    account = await api.metatrader_account_api.get_account(account_id)
    account_access_token = account.access_token
    print(account_access_token)

Alternatively, you can retrieve account access token via web UI on https://app.metaapi.cloud/accounts page (see `this video <https://youtu.be/PKYiDns6_xI>`_).

Managing MetaTrader accounts (API servers for MT accounts)
==========================================================
Before you can use the API you have to add an MT account to MetaApi and start an API server for it.

However, before you can create an account, you have to create a provisioning profile.

Managing provisioning profiles via web UI
-----------------------------------------
You can manage provisioning profiles here: https://app.metaapi.cloud/provisioning-profiles

Creating a provisioning profile via API
---------------------------------------
.. code-block:: python

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
    await provisioningProfile.upload_file('broker.srv', '/path/to/broker.srv')

Retrieving existing provisioning profiles via API
-------------------------------------------------
.. code-block:: python

    provisioningProfiles = await api.provisioning_profile_api.get_provisioning_profiles()
    provisioningProfile = await api.provisioning_profile_api.get_provisioning_profile('profileId')

Updating a provisioning profile via API
---------------------------------------
.. code-block:: python

    await provisioningProfile.update({'name': 'New name'})
    # for MT5, you should upload a servers.dat file
    await provisioningProfile.upload_file('servers.dat', '/path/to/servers.dat')
    # for MT4, you should upload an .srv file instead
    await provisioningProfile.upload_file('broker.srv', '/path/to/broker.srv')

Removing a provisioning profile
-------------------------------
.. code-block:: python

    await provisioningProfile.remove()

Managing MetaTrader accounts (API servers) via web UI
-----------------------------------------------------
You can manage MetaTrader accounts here: https://app.metaapi.cloud/accounts

Create a MetaTrader account (API server) via API
------------------------------------------------
.. code-block:: python

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

Retrieving existing accounts via API
------------------------------------
.. code-block:: python

    # filter and paginate accounts, see esdoc for full list of filter options available
    accounts = await api.metatraderAccountApi.getAccounts({
        'limit': 10,
        'offset': 0,
        'query': 'ICMarketsSC-MT5',
        'state': ['DEPLOYED']
    })
    # get accounts without filter (returns 1000 accounts max)
    accounts = await api.metatraderAccountApi.getAccounts();

Updating an existing account via API
------------------------------------
.. code-block:: python

    await account.update({
        'name': 'Trading account #1',
        'login': '1234567',
        # password can be investor password for read-only access
        'password': 'qwerty',
        'server': 'ICMarketsSC-Demo',
        # synchronizationMode can be 'automatic' for RPC access or 'user' if you
        # want to keep track of terminal state in real-time (e.g. if you are
        # developing a EA or trading strategy)
        'synchronizationMode': 'automatic'
    })

Removing an account
-------------------
.. code-block:: python

    await account.remove()

Deploying, undeploying and redeploying an account (API server) via API
----------------------------------------------------------------------
.. code-block:: python

    await account.deploy()
    await account.undeploy()
    await account.redeploy()

Access MetaTrader account via RPC API
=====================================
RPC API let you query the trading terminal state. You should use
RPC API if you develop trading monitoring apps like myfxbook or other
simple trading apps.

You should create your account with automatic synchronization mode if
all you need is RPC API.

Query account information, positions, orders and history via RPC API
--------------------------------------------------------------------
.. code-block:: python

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

Query contract specifications and quotes via RPC API
----------------------------------------------------
.. code-block:: python

    connection = await account.connect()

    await connection.wait_synchronized()

    # first, subscribe to market data
    await connection.subscribe_to_market_data('GBPUSD')

    # read contract specification
    print(await connection.get_symbol_specification('GBPUSD'))
    # read current price
    print(await connection.get_symbol_price('GBPUSD'))

Use real-time streaming API
---------------------------
Real-time streaming API is good for developing trading applications like trade copiers or automated trading strategies.
The API synchronizes the terminal state locally so that you can query local copy of the terminal state really fast.

In order to use this API you need to create an account with `user` synchronization mode.

Synchronizing and reading terminal state
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    account = await api.metatrader_account_api.get_account('accountId')

    # account.synchronization_mode must be equal to 'user' at this point

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

Overriding local history storage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
By default history is stored in memory only. You can override history storage to save trade history to a persistent storage like MongoDB database.

.. code-block:: python

    from metaapi_cloud_sdk import HistoryStorage

    class MongodbHistoryStorage(HistoryStorage):
        # implement the abstract methods, see MemoryHistoryStorage for sample
        # implementation

    historyStorage = MongodbHistoryStorage()

    # Note: if you will not specify history storage, then in-memory storage
    # will be used (instance of MemoryHistoryStorage)
    connection = await account.connect(historyStorage)

    # access history storage
    historyStorage = connection.history_storage;

    # invoke other methods provided by your history storage implementation
    print(await historyStorage.yourMethod())

Receiving synchronization events
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You can override SynchronizationListener in order to receive synchronization event notifications, such as account/position/order/history updates or symbol quote updates.

.. code-block:: python

    from metaapi_cloud_sdk import SynchronizationListener

    # receive synchronization event notifications
    # first, implement your listener
    class MySynchronizationListener(SynchronizationListener):
        # override abstract methods you want to receive notifications for

    # now add the listener
    listener = MySynchronizationListener()
    connection.add_synchronization_listener(listener)

    # remove the listener when no longer needed
    connection.remove_synchronization_listener(listener)

Retrieve contract specifications and quotes via streaming API
-------------------------------------------------------------
.. code-block:: python

    connection = await account.connect()

    await connection.wait_synchronized()

    # first, subscribe to market data
    await connection.subscribe_to_market_data('GBPUSD')

    # read constract specification
    print(terminalState.specification('EURUSD'))

    # read current price
    print(terminalState.price('EURUSD'))

Execute trades (both RPC and streaming APIs)
--------------------------------------------
.. code-block:: python

    connection = await account.connect()

    await connection.wait_synchronized()

    # trade
    print(await connection.create_market_buy_order('GBPUSD', 0.07, 0.9, 2.0, {'comment': 'comment',
                                                                              'clientId': 'TE_GBPUSD_7hyINWqAl'}))
    print(await connection.create_market_sell_order('GBPUSD', 0.07, 2.0, 0.9, {'comment': 'comment',
                                                                               'clientId': 'TE_GBPUSD_7hyINWqAl'}))
    print(await connection.create_limit_buy_order('GBPUSD', 0.07, 1.0, 0.9, 2.0, {'comment': 'comment',
                                                                                  'clientId': 'TE_GBPUSD_7hyINWqAl'}))
    print(await connection.create_limit_sell_order('GBPUSD', 0.07, 1.5, 2.0, 0.9, {'comment': 'comment',
                                                                                   'clientId': 'TE_GBPUSD_7hyINWqAl'}))
    print(await connection.create_stop_buy_order('GBPUSD', 0.07, 1.5, 0.9, 2.0, {'comment': 'comment',
                                                                                 'clientId': 'TE_GBPUSD_7hyINWqAl'}))
    print(await connection.create_stop_sell_order('GBPUSD', 0.07, 1.0, 2.0, 0.9, {'comment': 'comment',
                                                                                  'clientId': 'TE_GBPUSD_7hyINWqAl'}))
    print(await connection.modify_position('46870472', 2.0, 0.9))
    print(await connection.close_position_partially('46870472', 0.9))
    print(await connection.close_position('46870472'))
    print(await connection.close_positions_by_symbol('EURUSD'))
    print(await connection.modify_order('46870472', 1.0, 2.0, 0.9))
    print(await connection.cancel_order('46870472'))

    # if you need to, check the extra result information in stringCode and numericCode properties of the response
    result = await connection.create_market_buy_order('GBPUSD', 0.07, 0.9, 2.0, {'comment': 'comment',
                                                                                 'clientId': 'TE_GBPUSD_7hyINWqAl'})
    print('Trade successful, result code is ' + result['stringCode'])

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
