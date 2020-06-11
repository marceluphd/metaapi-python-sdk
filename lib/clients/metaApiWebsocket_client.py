from lib.clients.timeoutException import TimeoutException
from lib.clients.errorHandler import ValidationException, NotFoundException, InternalException, UnauthorizedException
from lib.clients.notSynchronizedException import NotSynchronizedException
from lib.clients.notConnectedException import NotConnectedException
from lib.clients.synchronizationListener import SynchronizationListener
import socketio
import asyncio
import math
import re
import time
from typing import List
from datetime import datetime
import random
import string
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


def format_date(date: datetime) -> str:
    """Converts date to format compatible with JS"""

    return date.isoformat(timespec='milliseconds') + 'Z'


class MetatraderAccountInformation:
    """MetaTrader account information (see https://metaapi.cloud/docs/client/models/metatraderAccountInformation/)"""

    broker: str
    """Broker name."""
    currency: str
    """Account base currency ISO code."""
    server: str
    """Broker server name."""
    balance: float
    """Account balance."""
    equity: float
    """Account liquidation value."""
    margin: float
    """Used margin."""
    freeMargin: float
    """Free margin."""
    leverage: float
    """Account leverage coefficient."""
    marginLevel: float
    """Margin level calculated as % of freeMargin/margin."""


class MetatraderPosition:
    """MetaTrader position"""

    id: int
    """Position id (ticket number)."""
    type: str
    """Position type (one of POSITION_TYPE_BUY, POSITION_TYPE_SELL)."""
    symbol: str
    """Position symbol."""
    magic: int
    """Position magic number, identifies the EA which opened the position."""
    time: datetime
    """Time position was opened at."""
    updateTime: datetime
    """Last position modification time."""
    openPrice: float
    """Position open price."""
    currentPrice: float
    """Current price."""
    currentTickValue: float
    """Current tick value."""
    stopLoss: float
    """Optional position stop loss price."""
    takeProfit: float
    """Optional position take profit price."""
    volume: float
    """Position volume."""
    swap: float
    """Position cumulative swap."""
    profit: float
    """Position cumulative profit."""
    comment: str
    """Optional position comment. The sum of the line lengths of the comment and the clientId
    must be less than or equal to 27. For more information see https://metaapi.cloud/docs/client/clientIdUsage/"""
    clientId: str
    """Optional client-assigned id. The id value can be assigned when submitting a trade and
    will be present on position, history orders and history deals related to the trade. You can use this field to bind
    your trades to objects in your application and then track trade progress. The sum of the line lengths of the
    comment and the clientId must be less than or equal to 27. For more information see
    https://metaapi.cloud/docs/client/clientIdUsage/"""
    unrealizedProfit: float
    """Profit of the part of the position which is not yet closed, including swap."""
    realizedProfit: float
    """Profit of the already closed part, including commissions and swap."""
    commission: float
    """Optional position commission."""


class MetatraderOrder:
    """MetaTrader order"""

    id: int
    """Order id (ticket number)."""
    type: str
    """Order type (one of ORDER_TYPE_SELL, ORDER_TYPE_BUY, ORDER_TYPE_BUY_LIMIT,
    ORDER_TYPE_SELL_LIMIT, ORDER_TYPE_BUY_STOP, ORDER_TYPE_SELL_STOP). See
    https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties#enum_order_type"""
    state: str
    """Order state one of (ORDER_STATE_STARTED, ORDER_STATE_PLACED, ORDER_STATE_CANCELED,
    ORDER_STATE_PARTIAL, ORDER_STATE_FILLED, ORDER_STATE_REJECTED, ORDER_STATE_EXPIRED, ORDER_STATE_REQUEST_ADD,
    ORDER_STATE_REQUEST_MODIFY, ORDER_STATE_REQUEST_CANCEL). See
    https://www.mql5.com/en/docs/constants/tradingconstants/orderproperties#enum_order_state"""
    magic: int
    """Order magic number, identifies the EA which created the order."""
    time: datetime
    """Time order was created at."""
    doneTime: datetime
    """optional time order was executed or canceled at. Will be specified for completed orders only"""
    symbol: str
    """Order symbol."""
    openPrice: float
    """Order open price (market price for market orders, limit price for limit orders or stop price for stop orders)."""
    currentPrice: float
    """Current price."""
    stopLoss: float
    """Optional order stop loss price."""
    takeProfit: float
    """Optional order take profit price."""
    volume: float
    """Order requested quantity."""
    currentVolume: float
    """Order remaining quantity, i.e. requested quantity - filled quantity."""
    positionId: str
    """Order position id. Present only if the order has a position attached to it."""
    comment: str
    """Optional order comment. The sum of the line lengths of the comment and the clientId
    must be less than or equal to 27. For more information see https://metaapi.cloud/docs/client/clientIdUsage/"""
    originalComment: str
    """Optional order original comment (present if possible to restore original comment from history)"""
    clientId: str
    """Optional client-assigned id. The id value can be assigned when submitting a trade and
    will be present on position, history orders and history deals related to the trade. You can use this field to bind
    your trades to objects in your application and then track trade progress. The sum of the line lengths of the
    comment and the clientId must be less than or equal to 27. For more information see
    https://metaapi.cloud/docs/client/clientIdUsage/"""
    platform: str
    """Platform id (mt4 or mt5)."""
    updatePending: bool
    """Optional flag indicating that order client id and original comment was not
    identified yet and will be updated in a future synchronization packet."""


class MetatraderHistoryOrders:
    """MetaTrader history orders search query response."""

    historyOrders: List[MetatraderOrder]
    """Array of history orders returned."""
    synchronizing: bool
    """Flag indicating that history order initial synchronization is still in progress 
    and thus search results may be incomplete"""


class MetatraderDeal:
    """MetaTrader deal"""

    id: str
    """Deal id (ticket number)"""
    type: str
    """deal type (one of DEAL_TYPE_BUY, DEAL_TYPE_SELL, DEAL_TYPE_BALANCE, DEAL_TYPE_CREDIT,
    DEAL_TYPE_CHARGE, DEAL_TYPE_CORRECTION, DEAL_TYPE_BONUS, DEAL_TYPE_COMMISSION, DEAL_TYPE_COMMISSION_DAILY,
    DEAL_TYPE_COMMISSION_MONTHLY, DEAL_TYPE_COMMISSION_AGENT_DAILY, DEAL_TYPE_COMMISSION_AGENT_MONTHLY,
    DEAL_TYPE_INTEREST, DEAL_TYPE_BUY_CANCELED, DEAL_TYPE_SELL_CANCELED, DEAL_DIVIDEND, DEAL_DIVIDEND_FRANKED,
    DEAL_TAX). See https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties#enum_deal_type"""
    entryType: str
    """Deal entry type (one of DEAL_ENTRY_IN, DEAL_ENTRY_OUT, DEAL_ENTRY_INOUT,
    DEAL_ENTRY_OUT_BY). See https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties#enum_deal_entry"""
    symbol: str
    """Optional symbol deal relates to."""
    magic: int
    """Optional deal magic number, identifies the EA which initiated the deal."""
    time: datetime
    """Time the deal was conducted at."""
    volume: float
    """Optional deal volume."""
    price: float
    """Optional, the price the deal was conducted at."""
    commission: float
    """Optional deal commission."""
    swap: float
    """Optional deal swap."""
    profit: float
    """Deal profit."""
    positionId: str
    """Optional id of position the deal relates to."""
    orderId: str
    """Optional id of order the deal relates to."""
    comment: str
    """Optional deal comment. The sum of the line lengths of the comment and the clientId
    must be less than or equal to 27. For more information see https://metaapi.cloud/docs/client/clientIdUsage/"""
    originalComment: str
    """Optional deal original comment (present if possible to restore original comment from history)."""
    clientId: str
    """Optional client-assigned id. The id value can be assigned when submitting a trade and will be present on 
    position, history orders and history deals related to the trade. You can use this field to bind your trades 
    to objects in your application and then track trade progress. The sum of the line lengths of the comment and 
    the clientId must be less than or equal to 27. For more information see 
    https://metaapi.cloud/docs/client/clientIdUsage/"""
    platform: str
    """Platform id (mt4 or mt5)."""
    updatePending: bool
    """optional flag indicating that deal client id and original comment was not
    identified yet and will be updated in a future synchronization packet"""


class MetatraderDeals:
    """MetaTrader history deals search query response"""

    deals: List[MetatraderDeal]
    """Array of history deals returned."""
    synchronizing: bool
    """Flag indicating that deal initial synchronization is still in progress
    and thus search results may be incomplete."""


class MetatraderSymbolSpecification:
    """MetaTrader symbol specification. Contains symbol specification (see
    https://metaapi.cloud/docs/client/models/metatraderSymbolSpecification/)"""

    symbol: str
    """Symbol (e.g. a currency pair or an index)."""
    tickSize: float
    """Tick size"""
    minVolume: float
    """Minimum order volume for the symbol."""
    maxVolume: float
    """Maximum order volume for the symbol."""
    volumeStep: float
    """Order volume step for the symbol."""


class MetatraderSymbolPrice:
    """MetaTrader symbol price. Contains current price for a symbol (see
    https://metaapi.cloud/docs/client/models/metatraderSymbolPrice/)"""

    symbol: str
    """Symbol (e.g. a currency pair or an index)."""
    bid: float
    """Bid price."""
    ask: float
    """Ask price."""
    profitTickValue: float
    """Tick value for a profitable position."""
    lossTickValue: float
    """Tick value for a loosing position."""


class MetaApiWebsocketClient:
    """MetaApi websocket API client (see https://metaapi.cloud/docs/client/websocket/overview/)"""

    def __init__(self, token: str, domain: str = 'agiliumtrade.agiliumtrade.ai'):
        """Inits MetaApi websocket API client instance.

        Args:
            token: Authorization token.
            domain: Domain to connect to, default is agiliumtrade.agiliumtrade.ai.
        """
        self._url = f'https://mt-client-api-v1.{domain}'
        self._token = token
        self._requestResolves = {}
        self._synchronizationListeners = {}
        self._connected = False
        self._socket = None
        self._reconnectListeners = []

    def set_url(self, url: str):
        """Patch server URL for use in unit tests

        Args:
            url: Patched server URL.
        """
        self._url = url

    async def connect(self) -> asyncio.Future:
        """Connects to MetaApi server via socket.io protocol

        Returns:
            A coroutine which resolves when connection is established.
        """
        if not self._connected:
            self._connected = True
            self._requestResolves = {}
            self._resolved = False
            result = asyncio.Future()

            url = f'{self._url}?auth-token={self._token}'
            self._socket = socketio.AsyncClient(reconnection=True, reconnection_delay=1000,
                                                reconnection_delay_max=5000, reconnection_attempts=math.inf)
            await self._socket.connect(url, socketio_path='ws')

            @self._socket.on('connect')
            async def on_connect():
                print(f'[{datetime.now().isoformat()}] MetaApi websocket client connected to the MetaApi server')
                if not self._resolved:
                    self._resolved = True
                    result.set_result()
                else:
                    await self._fire_reconnected()

                if not self._connected:
                    self._socket.disconnect()

            @self._socket.on('reconnect')
            async def on_reconnect():
                await self._fire_reconnected()

            @self._socket.on('connect_error')
            def on_connect_error(err):
                print(f'[{datetime.now().isoformat()}] MetaApi websocket client connection error', err)
                if not self._resolved:
                    self._resolved = True
                    result.set_exception(err)

            @self._socket.on('connect_timeout')
            def on_connect_timeout(timeout):
                print(f'[{datetime.now().isoformat()}] MetaApi websocket client connection timeout')
                if not self._resolved:
                    self._resolved = True
                    result.set_exception(TimeoutException('MetaApi websocket client connection timed out'))

            @self._socket.on('disconnect')
            async def on_disconnect(reason):
                print(f'[{datetime.now().isoformat()}] MetaApi websocket client disconnected from the MetaApi '
                      f'server because of {reason}')
                await self._reconnect()

            @self._socket.on('error')
            async def on_error(error):
                print(f'[{datetime.now().isoformat()}] MetaApi websocket client error', error)
                await self._reconnect()

            @self._socket.on('response')
            def on_response(data):
                if data['requestId'] in self._requestResolves:
                    request_resolve = self._requestResolves[data['requestId']]
                    del self._requestResolves[data['requestId']]
                else:
                    request_resolve = asyncio.Future()
                self._convert_iso_time_to_date(data)
                request_resolve.set_result(data)

            @self._socket.on('processingError')
            def on_processing_error(data):
                if data['requestId'] in self._requestResolves:
                    request_resolve = self._requestResolves[data['requestId']]
                    del self._requestResolves[data['requestId']]
                else:
                    request_resolve = asyncio.Future()
                request_resolve.set_exception(self._convert_error(data))

            @self._socket.on('synchronization')
            async def on_synchronization(data):
                self._convert_iso_time_to_date(data)
                await self._process_synchronization_packet(data)

            return result

    async def close(self):
        """Closes connection to MetaApi server"""
        if self._connected:
            self._connected = False
            await self._socket.disconnect()
            for request_resolve in self._requestResolves:
                self._requestResolves[request_resolve].set_exception(Exception('MetaApi connection closed'))
            self._requestResolves = {}
            self._synchronizationListeners = {}

    async def get_account_information(self, account_id: str) -> asyncio.Future:
        """Returns account information for a specified MetaTrader account
        (see https://metaapi.cloud/docs/client/websocket/api/readTradingTerminalState/readAccountInformation/).

        Args:
            account_id: Id of the MetaTrader account to return information for.

        Returns:
            A coroutine resolving with account information.
        """
        response = await self._rpc_request(account_id, {'type': 'getAccountInformation'})
        return response['accountInformation']

    async def get_positions(self, account_id: str) -> asyncio.Future:
        """Returns positions for a specified MetaTrader account
        (see https://metaapi.cloud/docs/client/websocket/api/readTradingTerminalState/readPositions/).

        Args:
            account_id: Id of the MetaTrader account to return information for.

        Returns:
            A coroutine resolving with array of open positions.
        """
        response = await self._rpc_request(account_id, {'type': 'getPositions'})
        return response['positions']

    async def get_position(self, account_id: str, position_id: str) -> asyncio.Future:
        """Returns specific position for a MetaTrader account
        (see https://metaapi.cloud/docs/client/websocket/api/readTradingTerminalState/readPosition/).

        Args:
            account_id: Id of the MetaTrader account to return information for.
            position_id: Position id.

        Returns:
            A coroutine resolving with MetaTrader position found.
        """
        response = await self._rpc_request(account_id, {'type': 'getPosition', 'positionId': position_id})
        return response['position']

    async def get_orders(self, account_id: str) -> asyncio.Future:
        """Returns open orders for a specified MetaTrader account
        (see https://metaapi.cloud/docs/client/websocket/api/readTradingTerminalState/readOrders/).

        Args:
            account_id: Id of the MetaTrader account to return information for.

        Returns:
            A coroutine resolving with open MetaTrader orders.
        """
        response = await self._rpc_request(account_id, {'type': 'getOrders'})
        return response['orders']

    async def get_order(self, account_id: str, order_id: str) -> asyncio.Future:
        """Returns specific open order for a MetaTrader account
        (see https://metaapi.cloud/docs/client/websocket/api/readTradingTerminalState/readOrder/).

        Args:
            account_id: Id of the MetaTrader account to return information for.
            order_id: Order id (ticket number).

        Returns:
            A coroutine resolving with metatrader order found.
        """
        response = await self._rpc_request(account_id, {'type': 'getOrder', 'orderId': order_id})
        return response['order']

    async def get_history_orders_by_ticket(self, account_id: str, ticket: str) -> dict:
        """Returns the history of completed orders for a specific ticket number
        (see https://metaapi.cloud/docs/client/websocket/api/retrieveHistoricalData/readHistoryOrdersByTicket/).

        Args:
            account_id: Id of the MetaTrader account to return information for.
            ticket: Ticket number (order id).

        Returns:
            A coroutine resolving with request results containing history orders found.
        """
        response = await self._rpc_request(account_id, {'type': 'getHistoryOrdersByTicket', 'ticket': ticket})
        return {
            'historyOrders': response['historyOrders'],
            'synchronizing': response['synchronizing']
        }

    async def get_history_orders_by_position(self, account_id: str, position_id: str) -> dict:
        """Returns the history of completed orders for a specific position id
        (see https://metaapi.cloud/docs/client/websocket/api/retrieveHistoricalData/readHistoryOrdersByPosition/)

        Args:
            account_id: Id of the MetaTrader account to return information for.
            position_id: Position id.

        Returns:
            A coroutine resolving with request results containing history orders found.
        """
        response = await self._rpc_request(account_id, {'type': 'getHistoryOrdersByPosition',
                                                        'positionId': position_id})
        return {
            'historyOrders': response['historyOrders'],
            'synchronizing': response['synchronizing']
        }

    async def get_history_orders_by_time_range(self, account_id: str, start_time: datetime, end_time: datetime,
                                               offset=0, limit=1000) -> dict:
        """Returns the history of completed orders for a specific time range
        (see https://metaapi.cloud/docs/client/websocket/api/retrieveHistoricalData/readHistoryOrdersByTimeRange/)

        Args:
            account_id: Id of the MetaTrader account to return information for.
            start_time: Start of time range, inclusive.
            end_time: End of time range, exclusive.
            offset: Pagination offset, default is 0.
            limit: Pagination limit, default is 1000.

        Returns:
            A coroutine resolving with request results containing history orders found.
        """
        response = await self._rpc_request(account_id, {'type': 'getHistoryOrdersByTimeRange',
                                                        'startTime': format_date(start_time),
                                                        'endTime': format_date(end_time),
                                                        'offset': offset, 'limit': limit})
        return {
            'historyOrders': response['historyOrders'],
            'synchronizing': response['synchronizing']
        }

    async def get_deals_by_ticket(self, account_id: str, ticket: str):
        """Returns history deals with a specific ticket number
        (see https://metaapi.cloud/docs/client/websocket/api/retrieveHistoricalData/readDealsByTicket/).

        Args:
            account_id: Id of the MetaTrader account to return information for.
            ticket: Ticket number (deal id for MT5 or order id for MT4).

        Returns:
            A coroutine resolving with request results containing deals found.
        """
        response = await self._rpc_request(account_id, {'type': 'getDealsByTicket', 'ticket': ticket})
        return {
            'deals': response['deals'],
            'synchronizing': response['synchronizing']
        }

    async def get_deals_by_position(self, account_id: str, position_id: str):
        """Returns history deals for a specific position id
        (see https://metaapi.cloud/docs/client/websocket/api/retrieveHistoricalData/readDealsByPosition/).

        Args:
            account_id: Id of the MetaTrader account to return information for.
            position_id: Position id.

        Returns:
            A coroutine resolving with request results containing deals found.
        """
        response = await self._rpc_request(account_id, {'type': 'getDealsByPosition', 'positionId': position_id})
        return {
            'deals': response['deals'],
            'synchronizing': response['synchronizing']
        }

    async def get_deals_by_time_range(self, account_id: str, start_time: datetime, end_time: datetime, offset: int = 0,
                                      limit: int = 1000):
        """Returns history deals with for a specific time range
        (see https://metaapi.cloud/docs/client/websocket/api/retrieveHistoricalData/readDealsByTimeRange/).

        Args:
            account_id: Id of the MetaTrader account to return information for.
            start_time: Start of time range, inclusive.
            end_time: End of time range, exclusive.
            offset: Pagination offset, default is 0.
            limit: Pagination limit, default is 1000.

        Returns:
            A coroutine resolving with request results containing deals found.
        """
        response = await self._rpc_request(account_id, {'type': 'getDealsByTimeRange',
                                                        'startTime': format_date(start_time),
                                                        'endTime': format_date(end_time),
                                                        'offset': offset, 'limit': limit})
        return {
            'deals': response['deals'],
            'synchronizing': response['synchronizing']
        }

    def remove_history(self, account_id: str):
        """Clears the order and transaction history of a specified account so that it can be synchronized from scratch
        (see https://metaapi.cloud/docs/client/websocket/api/removeHistory/).

        Args:
            account_id: Id of the MetaTrader account to remove history for.

        Returns:
            A coroutine resolving when the history is cleared.
        """
        return self._rpc_request(account_id, {'type': 'removeHistory'})

    async def trade(self, account_id: str, trade) -> asyncio.Future:
        """Execute a trade on a connected MetaTrader account
        (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            account_id: Id of the MetaTrader account to execute trade for.
            trade: Trade to execute (see docs for possible trade types).

        Returns:
            A coroutine resolving with trade result.
        """
        response = await self._rpc_request(account_id, {'type': 'trade', 'trade': trade})
        return response['response']

    def subscribe(self, account_id: str):
        """Subscribes to the Metatrader terminal events
        (see https://metaapi.cloud/docs/client/websocket/api/subscribe/).

        Args:
            account_id: Id of the MetaTrader account to subscribe to.

        Returns:
            A coroutine which resolves when subscription started.
        """
        return self._rpc_request(account_id, {'type': 'subscribe'})

    def reconnect(self, account_id: str):
        """Reconnects to the Metatrader terminal (see https://metaapi.cloud/docs/client/websocket/api/reconnect/).

        Args:
            account_id: Id of the MetaTrader account to reconnect.

        Returns:
            A coroutine which resolves when reconnection started
        """
        return self._rpc_request(account_id, {'type': 'reconnect'})

    def synchronize(self, account_id: str, starting_history_order_time: datetime, starting_deal_time: datetime):
        """Requests the terminal to start synchronization process. Use it if user synchronization mode is set to user
        for the account (see https://metaapi.cloud/docs/client/websocket/synchronizing/synchronize/).

        Args:
            account_id: Id of the MetaTrader account to synchronize.
            starting_history_order_time: From what date to start synchronizing history orders from. If not specified,
            the entire order history will be downloaded.
            starting_deal_time: From what date to start deal synchronization from. If not specified, then all
            history deals will be downloaded.

        Returns:
            A coroutine which resolves when synchronization is started.
        """
        return self._rpc_request(account_id, {'type': 'synchronize',
                                              'startingHistoryOrderTime': format_date(starting_history_order_time),
                                              'startingDealTime': format_date(starting_deal_time)})

    def subscribe_to_market_data(self, account_id: str, symbol: str):
        """Subscribes on market data of specified symbol
        (see https://metaapi.cloud/docs/client/websocket/marketDataStreaming/subscribeToMarketData/).

        Args:
            account_id: Id of the MetaTrader account.
            symbol: Symbol (e.g. currency pair or an index).

        Returns:
            A coroutine which resolves when subscription request was processed.
        """
        return self._rpc_request(account_id, {'type': 'subscribeToMarketData', 'symbol': symbol})

    async def get_symbol_specification(self, account_id: str, symbol: str) -> asyncio.Future:
        """Retrieves specification for a symbol
        (see https://metaapi.cloud/docs/client/websocket/api/retrieveMarketData/getSymbolSpecification/).

        Args:
            account_id: Id of the MetaTrader account to retrieve symbol specification for.
            symbol: Symbol to retrieve specification for.

        Returns:
            A coroutine which resolves when specification is retrieved.
        """
        response = await self._rpc_request(account_id, {'type': 'getSymbolSpecification', 'symbol': symbol})
        return response['specification']

    async def get_symbol_price(self, account_id: str, symbol: str) -> asyncio.Future:
        """Retrieves price for a symbol
        (see https://metaapi.cloud/docs/client/websocket/api/retrieveMarketData/getSymbolPrice/).

        Args:
            account_id: Id of the MetaTrader account to retrieve symbol price for.
            symbol: Symbol to retrieve price for.

        Returns:
            A coroutine which resolves when price is retrieved.
        """
        response = await self._rpc_request(account_id, {'type': 'getSymbolPrice', 'symbol': symbol})
        return response['price']

    def add_synchronization_listener(self, account_id: str, listener):
        """Adds synchronization listener for specific account.

        Args:
            account_id: Account id.
            listener: Synchronization listener to add.
        """
        if account_id in self._synchronizationListeners:
            listeners = self._synchronizationListeners[account_id]
        else:
            listeners = []
            self._synchronizationListeners[account_id] = listeners
        listeners.append(listener)

    def remove_synchronization_listener(self, account_id: str, listener: SynchronizationListener):
        """Removes synchronization listener for specific account.

        Args:
            account_id: Account id.
            listener: Synchronization listener to remove.
        """
        listeners = self._synchronizationListeners[account_id]

        if not listeners:
            listeners = []
        elif listeners.__contains__(listener):
            listeners.remove(listener)
        self._synchronizationListeners[account_id] = listeners

    def add_reconnect_listener(self, listener):
        """Adds reconnect listener.

        Args:
            listener: Reconnect listener to add.
        """

        self._reconnectListeners.append(listener)

    def remove_reconnect_listener(self, listener):
        """Removes reconnect listener.

        Args:
            listener: Listener to remove.
        """

        if self._reconnectListeners.__contains__(listener):
            self._reconnectListeners.remove(listener)

    def remove_all_listeners(self):
        """Removes all listeners. Intended for use in unit tests."""

        self._synchronizationListeners = {}
        self._reconnectListeners = []

    async def _reconnect(self):
        while (not self._socket.connected) and self._connected:
            time.sleep(1)
            await self._socket.connect()

    async def _rpc_request(self, account_id: str, request: dict):
        if not self._connected:
            await self.connect()

        request_id = ''.join(random.choice(string.ascii_lowercase) for i in range(32))

        self._requestResolves[request_id] = asyncio.Future()
        request['accountId'] = account_id
        request['requestId'] = request_id
        await self._socket.emit('request', request)
        return await self._requestResolves[request_id]

    def _convert_error(self, data) -> Exception:
        if data['error'] == 'ValidationError':
            return ValidationException(data['message'], data['details'])
        elif data['error'] == 'NotFoundError':
            return NotFoundException(data['message'])
        elif data['error'] == 'NotSynchronizedError':
            return NotSynchronizedException(data['message'])
        elif data['error'] == 'NotAuthenticatedError':
            return NotConnectedException(data['message'])
        elif data['error'] == 'UnauthorizedError':
            self.close()
            return UnauthorizedException(data['message'])
        else:
            return InternalException(data['message'])

    def _convert_iso_time_to_date(self, packet):
        if not isinstance(packet, str):
            for field in packet:
                value = packet[field]
                if isinstance(value, str) and re.search('time | Time', field):
                    packet[field] = datetime.strptime(value, DATE_FORMAT)
                if isinstance(value, list):
                    for item in value:
                        self._convert_iso_time_to_date(item)
                if isinstance(value, dict):
                    self._convert_iso_time_to_date(value)

    async def _process_synchronization_packet(self, data):
        try:
            if data['type'] == 'authenticated' and (data['accountId'] in self._synchronizationListeners):
                for listener in self._synchronizationListeners[data['accountId']]:
                    try:
                        await listener['onConnected']()
                    except Exception as err:
                        print('Failed to notify listener about connected event', err)
            elif data['type'] == 'disconnected' and (data['accountId'] in self._synchronizationListeners):
                for listener in self._synchronizationListeners[data['accountId']]:
                    try:
                        await listener['onDisconnected']()
                    except Exception as err:
                        print('Failed to notify listener about disconnected event', err)
            elif data['type'] == 'accountInformation':
                if data['accountInformation'] and (data['accountId'] in self._synchronizationListeners):
                    for listener in self._synchronizationListeners[data['accountId']]:
                        try:
                            await listener['onAccountInformationUpdated'](data['accountInformation'])
                        except Exception as err:
                            print('Failed to notify listener about accountInformation event', err)
            elif data['type'] == 'deals' and ('deals' in data):
                for deal in data['deals']:
                    if data['accountId'] in self._synchronizationListeners:
                        for listener in self._synchronizationListeners[data['accountId']]:
                            try:
                                await listener['onDealAdded'](deal)
                            except Exception as err:
                                print('Failed to notify listener about deals event', err)
            elif data['type'] == 'orders' and ('orders' in data):
                for order in data['orders']:
                    if data['accountId'] in self._synchronizationListeners:
                        for listener in self._synchronizationListeners[data['accountId']]:
                            try:
                                await listener['onOrderUpdated'](order)
                            except Exception as err:
                                print('Failed to notify listener about orders event', err)
            elif data['type'] == 'historyOrders' and ('historyOrders' in data):
                for historyOrder in data['historyOrders']:
                    if data['accountId'] in self._synchronizationListeners:
                        for listener in self._synchronizationListeners[data['accountId']]:
                            try:
                                await listener['onHistoryOrderAdded'](historyOrder)
                            except Exception as err:
                                print('Failed to notify listener about historyOrders event', err)
            elif data['type'] == 'positions' and ('positions' in data):
                for position in data['positions']:
                    if data['accountId'] in self._synchronizationListeners:
                        for listener in self._synchronizationListeners[data['accountId']]:
                            try:
                                await listener['onPositionUpdated'](position)
                            except Exception as err:
                                print('Failed to notify listener about positions event', err)
            elif data['type'] == 'update':
                if 'accountInformation' in data and (data['accountId'] in self._synchronizationListeners):
                    for listener in self._synchronizationListeners[data['accountId']]:
                        try:
                            await listener['onAccountInformationUpdated'](data['accountInformation'])
                        except Exception as err:
                            print('Failed to notify listener about update event', err)
                if 'updatedPositions' in data:
                    for position in data['updatedPositions']:
                        if data['accountId'] in self._synchronizationListeners:
                            for listener in self._synchronizationListeners[data['accountId']]:
                                try:
                                    await listener['onPositionUpdated'](position)
                                except Exception as err:
                                    print('Failed to notify listener about update event', err)
                if 'removedPositionIds' in data:
                    for positionId in data['removedPositionIds']:
                        if data['accountId'] in self._synchronizationListeners:
                            for listener in self._synchronizationListeners[data['accountId']]:
                                try:
                                    await listener['onPositionRemoved'](positionId)
                                except Exception as err:
                                    print('Failed to notify listener about update event', err)
                if 'updatedOrders' in data:
                    for order in data['updatedOrders']:
                        if data['accountId'] in self._synchronizationListeners:
                            for listener in self._synchronizationListeners[data['accountId']]:
                                try:
                                    await listener['onOrderUpdated'](order)
                                except Exception as err:
                                    print('Failed to notify listener about update event', err)
                if 'completedOrderIds' in data:
                    for orderId in data['completedOrderIds']:
                        if data['accountId'] in self._synchronizationListeners:
                            for listener in self._synchronizationListeners[data['accountId']]:
                                try:
                                    await listener['onOrderCompleted'](orderId)
                                except Exception as err:
                                    print('Failed to notify listener about update event', err)
                if 'historyOrders' in data:
                    for historyOrder in data['historyOrders']:
                        if data['accountId'] in self._synchronizationListeners:
                            for listener in self._synchronizationListeners[data['accountId']]:
                                try:
                                    await listener['onHistoryOrderAdded'](historyOrder)
                                except Exception as err:
                                    print('Failed to notify listener about update event', err)
                if 'deals' in data:
                    for deal in data['deals']:
                        if data['accountId'] in self._synchronizationListeners:
                            for listener in self._synchronizationListeners[data['accountId']]:
                                try:
                                    await listener['onDealAdded'](deal)
                                except Exception as err:
                                    print('Failed to notify listener about update event', err)
            elif data['type'] == 'dealSynchronizationFinished':
                if data['accountId'] in self._synchronizationListeners:
                    for listener in self._synchronizationListeners[data['accountId']]:
                        try:
                            await listener['onDealSynchronizationFinished']()
                        except Exception as err:
                            print('Failed to notify listener about dealSynchronizationFinished event', err)
            elif data['type'] == 'orderSynchronizationFinished':
                if data['accountId'] in self._synchronizationListeners:
                    for listener in self._synchronizationListeners[data['accountId']]:
                        try:
                            await listener['onOrderSynchronizationFinished']()
                        except Exception as err:
                            print('Failed to notify listener about orderSynchronizationFinished event', err)
            elif data['type'] == 'status':
                if data['accountId'] in self._synchronizationListeners:
                    for listener in self._synchronizationListeners[data['accountId']]:
                        try:
                            await listener['onBrokerConnectionStatusChanged'](bool(data['connected']))
                        except Exception as err:
                            print('Failed to notify listener about brokerConnectionStatusChanged event', err)
            elif data['type'] == 'specifications' and ('specifications' in data):
                for specification in data['specifications']:
                    if data['accountId'] in self._synchronizationListeners:
                        for listener in self._synchronizationListeners[data['accountId']]:
                            try:
                                await listener['onSymbolSpecificationUpdated'](specification)
                            except Exception as err:
                                print('Failed to notify listener about specifications event', err)
            elif data['type'] == 'prices' and ('prices' in data):
                for price in data['prices']:
                    if data['accountId'] in self._synchronizationListeners:
                        for listener in self._synchronizationListeners[data['accountId']]:
                            try:
                                await listener['onSymbolPriceUpdated'](price)
                            except Exception as err:
                                print('Failed to notify listener about prices event', err)
        except Exception as err:
            print('Failed to process incoming synchronization packet', err)

    async def _fire_reconnected(self):
        for listener in self._reconnectListeners:
            try:
                await listener.onReconnected()
            except Exception as err:
                print(f'[{datetime.now().isoformat()}] Failed to notify reconnect listener', err)
