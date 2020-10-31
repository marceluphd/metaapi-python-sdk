from ..clients.metaApi.synchronizationListener import SynchronizationListener
from ..clients.metaApi.reconnectListener import ReconnectListener
from ..clients.metaApi.metaApiWebsocket_client import MetaApiWebsocketClient
from .terminalState import TerminalState
from .memoryHistoryStorage import MemoryHistoryStorage
from .metatraderAccountModel import MetatraderAccountModel
from .connectionRegistryModel import ConnectionRegistryModel
from .historyStorage import HistoryStorage
from ..clients.timeoutException import TimeoutException
from .models import random_id, MetatraderSymbolSpecification, MetatraderAccountInformation, \
    MetatraderPosition, MetatraderOrder, MetatraderHistoryOrders, MetatraderDeals, MetatraderTradeResponse, \
    MetatraderSymbolPrice, MarketTradeOptions, PendingTradeOptions
from datetime import datetime, timedelta
from typing import Coroutine, List, TypedDict, Optional
import pytz
import asyncio


class SynchronizationOptions(TypedDict):
    applicationPattern: Optional[str]
    """Application regular expression pattern, default is .*"""
    synchronizationId: Optional[str]
    """synchronization id, last synchronization request id will be used by default"""
    timeoutInSeconds: Optional[float]
    """Wait timeout in seconds, default is 5m."""
    intervalInMilliseconds: Optional[float]
    """Interval between account reloads while waiting for a change, default is 1s."""


class MetaApiConnection(SynchronizationListener, ReconnectListener):
    """Exposes MetaApi MetaTrader API connection to consumers."""

    def __init__(self, websocket_client: MetaApiWebsocketClient, account: MetatraderAccountModel,
                 history_storage: HistoryStorage or None, connection_registry: ConnectionRegistryModel,
                 history_start_time: datetime = None):
        """Inits MetaApi MetaTrader Api connection.

        Args:
            websocket_client: MetaApi websocket client.
            account: MetaTrader account id to connect to.
            history_storage: Local terminal history storage. By default an instance of MemoryHistoryStorage
            will be used.
            history_start_time: History start sync time.
        """
        super().__init__()
        self._websocketClient = websocket_client
        self._account = account
        self._synchronized = False
        self._closed = False
        self._ordersSynchronized = {}
        self._dealsSynchronized = {}
        self._lastSynchronizationId = None
        self._lastDisconnectedSynchronizationId = None
        self._connection_registry = connection_registry
        self._history_start_time = history_start_time
        self._terminalState = TerminalState()
        self._historyStorage = history_storage or MemoryHistoryStorage(account.id)
        self._websocketClient.add_synchronization_listener(account.id, self)
        self._websocketClient.add_synchronization_listener(account.id, self._terminalState)
        self._websocketClient.add_synchronization_listener(account.id, self._historyStorage)
        self._websocketClient.add_reconnect_listener(self)

    def get_account_information(self) -> 'Coroutine[asyncio.Future[MetatraderAccountInformation]]':
        """Returns account information (see
        https://metaapi.cloud/docs/client/websocket/api/readTradingTerminalState/readAccountInformation/).

        Returns:
            A coroutine resolving with account information.
        """
        return self._websocketClient.get_account_information(self._account.id)

    def get_positions(self) -> 'Coroutine[asyncio.Future[List[MetatraderPosition]]]':
        """Returns positions (see
        https://metaapi.cloud/docs/client/websocket/api/readTradingTerminalState/readPositions/).

        Returns:
            A coroutine resolving with array of open positions.
        """
        return self._websocketClient.get_positions(self._account.id)

    def get_position(self, position_id: str) -> 'Coroutine[asyncio.Future[MetatraderPosition]]':
        """Returns specific position (see
        https://metaapi.cloud/docs/client/websocket/api/readTradingTerminalState/readPosition/).

        Args:
            position_id: Position id.

        Returns:
            A coroutine resolving with MetaTrader position found.
        """
        return self._websocketClient.get_position(self._account.id, position_id)

    def get_orders(self) -> 'Coroutine[asyncio.Future[List[MetatraderOrder]]]':
        """Returns open orders (see
        https://metaapi.cloud/docs/client/websocket/api/readTradingTerminalState/readOrders/).

        Returns:
            A coroutine resolving with open MetaTrader orders.
        """
        return self._websocketClient.get_orders(self._account.id)

    def get_order(self, order_id: str) -> 'Coroutine[asyncio.Future[MetatraderOrder]]':
        """Returns specific open order (see
        https://metaapi.cloud/docs/client/websocket/api/readTradingTerminalState/readOrder/).

        Args:
            order_id: Order id (ticket number).

        Returns:
            A coroutine resolving with metatrader order found.
        """
        return self._websocketClient.get_order(self._account.id, order_id)

    def get_history_orders_by_ticket(self, ticket: str) -> 'Coroutine[MetatraderHistoryOrders]':
        """Returns the history of completed orders for a specific ticket number (see
        https://metaapi.cloud/docs/client/websocket/api/retrieveHistoricalData/readHistoryOrdersByTicket/).

        Args:
            ticket: Ticket number (order id).

        Returns:
            A coroutine resolving with request results containing history orders found.
        """
        return self._websocketClient.get_history_orders_by_ticket(self._account.id, ticket)

    def get_history_orders_by_position(self, position_id: str) -> 'Coroutine[MetatraderHistoryOrders]':
        """Returns the history of completed orders for a specific position id (see
        https://metaapi.cloud/docs/client/websocket/api/retrieveHistoricalData/readHistoryOrdersByPosition/)

        Args:
            position_id: Position id.

        Returns:
            A coroutine resolving with request results containing history orders found.
        """
        return self._websocketClient.get_history_orders_by_position(self._account.id, position_id)

    def get_history_orders_by_time_range(self, start_time: datetime, end_time: datetime, offset: int = 0,
                                         limit: int = 1000) -> 'Coroutine[MetatraderHistoryOrders]':
        """Returns the history of completed orders for a specific time range (see
        https://metaapi.cloud/docs/client/websocket/api/retrieveHistoricalData/readHistoryOrdersByTimeRange/)

        Args:
            start_time: Start of time range, inclusive.
            end_time: End of time range, exclusive.
            offset: Pagination offset, default is 0.
            limit: Pagination limit, default is 1000.

        Returns:
            A coroutine resolving with request results containing history orders found.
        """
        return self._websocketClient.get_history_orders_by_time_range(self._account.id, start_time, end_time,
                                                                      offset, limit)

    def get_deals_by_ticket(self, ticket: str) -> 'Coroutine[MetatraderDeals]':
        """Returns history deals with a specific ticket number (see
        https://metaapi.cloud/docs/client/websocket/api/retrieveHistoricalData/readDealsByTicket/).

        Args:
            ticket: Ticket number (deal id for MT5 or order id for MT4).

        Returns:
            A coroutine resolving with request results containing deals found.
        """
        return self._websocketClient.get_deals_by_ticket(self._account.id, ticket)

    def get_deals_by_position(self, position_id) -> 'Coroutine[MetatraderDeals]':
        """Returns history deals for a specific position id (see
        https://metaapi.cloud/docs/client/websocket/api/retrieveHistoricalData/readDealsByPosition/).

        Args:
            position_id: Position id.

        Returns:
            A coroutine resolving with request results containing deals found.
        """
        return self._websocketClient.get_deals_by_position(self._account.id, position_id)

    def get_deals_by_time_range(self, start_time: datetime, end_time: datetime, offset: int = 0,
                                limit: int = 1000) -> 'Coroutine[MetatraderDeals]':
        """Returns history deals with for a specific time range (see
        https://metaapi.cloud/docs/client/websocket/api/retrieveHistoricalData/readDealsByTimeRange/).

        Args:
            start_time: Start of time range, inclusive.
            end_time: End of time range, exclusive.
            offset: Pagination offset, default is 0.
            limit: Pagination limit, default is 1000.

        Returns:
            A coroutine resolving with request results containing deals found.
        """
        return self._websocketClient.get_deals_by_time_range(self._account.id, start_time, end_time, offset, limit)

    def remove_history(self) -> Coroutine:
        """Clears the order and transaction history of a specified account so that it can be synchronized from scratch
        (see https://metaapi.cloud/docs/client/websocket/api/removeHistory/).

        Returns:
            A coroutine resolving when the history is cleared.
        """
        self._historyStorage.reset()
        return self._websocketClient.remove_history(self._account.id)

    def remove_application(self):
        """Clears the order and transaction history of a specified application and removes application (see
        https://metaapi.cloud/docs/client/websocket/api/removeApplication/).

        Returns:
            A coroutine resolving when the history is cleared and application is removed.
        """
        self._historyStorage.reset()
        return self._websocketClient.remove_application(self._account.id)

    def create_market_buy_order(self, symbol: str, volume: float, stop_loss: float = None, take_profit: float = None,
                                options: MarketTradeOptions = None) -> \
            'Coroutine[asyncio.Future[MetatraderTradeResponse]]':
        """Creates a market buy order (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            symbol: Symbol to trade.
            volume: Order volume.
            stop_loss: Optional stop loss price.
            take_profit: Optional take profit price.
            options: Optional trade options.

        Returns:
            A coroutine resolving with trade result.

        Raises:
            TradeException: On trade error.
        """
        trade_params = {'actionType': 'ORDER_TYPE_BUY', 'symbol': symbol, 'volume': volume}
        if stop_loss:
            trade_params['stopLoss'] = stop_loss
        if take_profit:
            trade_params['takeProfit'] = take_profit
        trade_params.update(options or {})
        return self._websocketClient.trade(self._account.id, trade_params)

    def create_market_sell_order(self, symbol: str, volume: float, stop_loss: float = None, take_profit: float = None,
                                 options: MarketTradeOptions = None) -> \
            'Coroutine[asyncio.Future[MetatraderTradeResponse]]':
        """Creates a market sell order (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            symbol: Symbol to trade.
            volume: Order volume.
            stop_loss: Optional stop loss price.
            take_profit: Optional take profit price.
            options: Optional trade options.

        Returns:
            A coroutine resolving with trade result.

        Raises:
            TradeException: On trade error.
        """
        trade_params = {'actionType': 'ORDER_TYPE_SELL', 'symbol': symbol, 'volume': volume}
        if stop_loss:
            trade_params['stopLoss'] = stop_loss
        if take_profit:
            trade_params['takeProfit'] = take_profit
        trade_params.update(options or {})
        return self._websocketClient.trade(self._account.id, trade_params)

    def create_limit_buy_order(self, symbol: str, volume: float, open_price: float, stop_loss: float = None,
                               take_profit: float = None, options: PendingTradeOptions = None) -> \
            'Coroutine[asyncio.Future[MetatraderTradeResponse]]':
        """Creates a limit buy order (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            symbol: Symbol to trade.
            volume: Order volume.
            open_price: Order limit price.
            stop_loss: Optional stop loss price.
            take_profit: Optional take profit price.
            options: Optional trade options.

        Returns:
            A coroutine resolving with trade result.

        Raises:
            TradeException: On trade error.
        """
        trade_params = {'actionType': 'ORDER_TYPE_BUY_LIMIT', 'symbol': symbol, 'volume': volume,
                        'openPrice': open_price}
        if stop_loss:
            trade_params['stopLoss'] = stop_loss
        if take_profit:
            trade_params['takeProfit'] = take_profit
        trade_params.update(options or {})
        return self._websocketClient.trade(self._account.id, trade_params)

    def create_limit_sell_order(self, symbol: str, volume: float, open_price: float, stop_loss: float = None,
                                take_profit: float = None, options: PendingTradeOptions = None) -> \
            'Coroutine[asyncio.Future[MetatraderTradeResponse]]':
        """Creates a limit sell order (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            symbol: Symbol to trade.
            volume: Order volume.
            open_price: Order limit price.
            stop_loss: Optional stop loss price.
            take_profit: Optional take profit price.
            options: Optional trade options.

        Returns:
            A coroutine resolving with trade result.

        Raises:
            TradeException: On trade error.
        """
        trade_params = {'actionType': 'ORDER_TYPE_SELL_LIMIT', 'symbol': symbol, 'volume': volume,
                        'openPrice': open_price}
        if stop_loss:
            trade_params['stopLoss'] = stop_loss
        if take_profit:
            trade_params['takeProfit'] = take_profit
        trade_params.update(options or {})
        return self._websocketClient.trade(self._account.id, trade_params)

    def create_stop_buy_order(self, symbol: str, volume: float, open_price: float, stop_loss: float = None,
                              take_profit: float = None, options: PendingTradeOptions = None) -> \
            'Coroutine[asyncio.Future[MetatraderTradeResponse]]':
        """Creates a stop buy order (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            symbol: Symbol to trade.
            volume: Order volume.
            open_price: Order limit price.
            stop_loss: Optional stop loss price.
            take_profit: Optional take profit price.
            options: Optional trade options.

        Returns:
            A coroutine resolving with trade result.

        Raises:
            TradeException: On trade error.
        """
        trade_params = {'actionType': 'ORDER_TYPE_BUY_STOP', 'symbol': symbol, 'volume': volume,
                        'openPrice': open_price}
        if stop_loss:
            trade_params['stopLoss'] = stop_loss
        if take_profit:
            trade_params['takeProfit'] = take_profit
        trade_params.update(options or {})
        return self._websocketClient.trade(self._account.id, trade_params)

    def create_stop_sell_order(self, symbol: str, volume: float, open_price: float, stop_loss: float = None,
                               take_profit: float = None, options: PendingTradeOptions = None) -> \
            'Coroutine[asyncio.Future[MetatraderTradeResponse]]':
        """Creates a stop sell order (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            symbol: Symbol to trade.
            volume: Order volume.
            open_price: Order limit price.
            stop_loss: Optional stop loss price.
            take_profit: Optional take profit price.
            options: Optional trade options.

        Returns:
            A coroutine resolving with trade result.

        Raises:
            TradeException: On trade error.
        """
        trade_params = {'actionType': 'ORDER_TYPE_SELL_STOP', 'symbol': symbol, 'volume': volume,
                        'openPrice': open_price}
        if stop_loss:
            trade_params['stopLoss'] = stop_loss
        if take_profit:
            trade_params['takeProfit'] = take_profit
        trade_params.update(options or {})
        return self._websocketClient.trade(self._account.id, trade_params)

    def modify_position(self, position_id: str, stop_loss: float = None, take_profit: float = None) -> \
            'Coroutine[asyncio.Future[MetatraderTradeResponse]]':
        """Modifies a position (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            position_id: Position id to modify.
            stop_loss: Optional stop loss price.
            take_profit: Optional take profit price.

        Returns:
            A coroutine resolving with trade result.

        Raises:
            TradeException: On trade error.
        """
        trade_params = {'actionType': 'POSITION_MODIFY', 'positionId': position_id}
        if stop_loss:
            trade_params['stopLoss'] = stop_loss
        if take_profit:
            trade_params['takeProfit'] = take_profit
        return self._websocketClient.trade(self._account.id, trade_params)

    def close_position_partially(self, position_id: str, volume: float, options: MarketTradeOptions = None) -> \
            'Coroutine[asyncio.Future[MetatraderTradeResponse]]':
        """Partially closes a position (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            position_id: Position id to modify.
            volume: Volume to close.
            options: Optional trade options.

        Returns:
            A coroutine resolving with trade result.

        Raises:
            TradeException: On trade error.
        """
        trade_params = {'actionType': 'POSITION_PARTIAL', 'positionId': position_id, 'volume': volume}
        trade_params.update(options or {})
        return self._websocketClient.trade(self._account.id, trade_params)

    def close_position(self, position_id: str, options: MarketTradeOptions = None) -> \
            'Coroutine[asyncio.Future[MetatraderTradeResponse]]':
        """Fully closes a position (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            position_id: Position id to modify.
            options: Optional trade options.

        Returns:
            A coroutine resolving with trade result.

        Raises:
            TradeException: On trade error.
        """
        trade_params = {'actionType': 'POSITION_CLOSE_ID', 'positionId': position_id}
        trade_params.update(options or {})
        return self._websocketClient.trade(self._account.id, trade_params)

    def close_positions_by_symbol(self, symbol: str, options: MarketTradeOptions = None) -> \
            'Coroutine[asyncio.Future[MetatraderTradeResponse]]':
        """Closes positions by a symbol (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            symbol: Symbol to trade.
            options: Optional trade options.

        Returns:
            A coroutine resolving with trade result.

        Raises:
            TradeException: On trade error.
        """
        trade_params = {'actionType': 'POSITIONS_CLOSE_SYMBOL', 'symbol': symbol}
        trade_params.update(options or {})
        return self._websocketClient.trade(self._account.id, trade_params)

    def modify_order(self, order_id: str, open_price: float, stop_loss: float = None,
                     take_profit: float = None) -> \
            'Coroutine[asyncio.Future[MetatraderTradeResponse]]':
        """Modifies a pending order (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            order_id: Order id (ticket number).
            open_price: Order stop price.
            stop_loss: Optional stop loss price.
            take_profit: Optional take profit price.

        Returns:
            A coroutine resolving with trade result.

        Raises:
            TradeException: On trade error.
        """
        trade_params = {'actionType': 'ORDER_MODIFY', 'orderId': order_id, 'openPrice': open_price}
        if stop_loss:
            trade_params['stopLoss'] = stop_loss
        if take_profit:
            trade_params['takeProfit'] = take_profit
        return self._websocketClient.trade(self._account.id, trade_params)

    def cancel_order(self, order_id: str) -> \
            'Coroutine[asyncio.Future[MetatraderTradeResponse]]':
        """Cancels order (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            order_id: Order id (ticket number).

        Returns:
            A coroutine resolving with trade result.

        Raises:
            TradeException: On trade error.
        """
        return self._websocketClient.trade(self._account.id, {'actionType': 'ORDER_CANCEL', 'orderId': order_id})

    def reconnect(self) -> Coroutine:
        """Reconnects to the Metatrader terminal (see https://metaapi.cloud/docs/client/websocket/api/reconnect/).

        Returns:
            A coroutine which resolves when reconnection started.
        """
        return self._websocketClient.reconnect(self._account.id)

    async def synchronize(self) -> Coroutine:
        """Requests the terminal to start synchronization process.
        (see https://metaapi.cloud/docs/client/websocket/synchronizing/synchronize/).

        Returns:
            A coroutine which resolves when synchronization started.
        """
        starting_history_order_time = \
            datetime.utcfromtimestamp(max(((self._history_start_time and self._history_start_time.timestamp()) or 0),
                                      (await self._historyStorage.last_history_order_time()).timestamp()))\
            .replace(tzinfo=pytz.UTC)
        starting_deal_time = \
            datetime.utcfromtimestamp(max(((self._history_start_time and self._history_start_time.timestamp()) or 0),
                                      (await self._historyStorage.last_deal_time()).timestamp()))\
            .replace(tzinfo=pytz.UTC)
        synchronization_id = random_id()
        self._lastSynchronizationId = synchronization_id
        return await self._websocketClient.synchronize(self._account.id, synchronization_id,
                                                       starting_history_order_time, starting_deal_time)

    async def initialize(self):
        """Initializes meta api connection"""
        await self._historyStorage.load_data_from_disk()

    async def subscribe(self) -> Coroutine:
        """Initiates subscription to MetaTrader terminal.

        Returns:
            A coroutine which resolves when subscription is initiated.
        """
        return self._websocketClient.subscribe(self._account.id)

    def subscribe_to_market_data(self, symbol: str) -> Coroutine:
        """Subscribes on market data of specified symbol (see
        https://metaapi.cloud/docs/client/websocket/marketDataStreaming/subscribeToMarketData/).

        Args:
            symbol: Symbol (e.g. currency pair or an index).

        Returns:
            Promise which resolves when subscription request was processed.
        """
        return self._websocketClient.subscribe_to_market_data(self._account.id, symbol)

    def get_symbol_specification(self, symbol: str) -> 'Coroutine[asyncio.Future[MetatraderSymbolSpecification]]':
        """Retrieves specification for a symbol (see
        https://metaapi.cloud/docs/client/websocket/api/retrieveMarketData/getSymbolSpecification/).

        Args:
            symbol: Symbol to retrieve specification for.

        Returns:
            A coroutine which resolves when specification MetatraderSymbolSpecification is retrieved.
        """
        return self._websocketClient.get_symbol_specification(self._account.id, symbol)

    def get_symbol_price(self, symbol) -> 'Coroutine[asyncio.Future[MetatraderSymbolPrice]]':
        """Retrieves specification for a symbol (see
        https://metaapi.cloud/docs/client/websocket/api/retrieveMarketData/getSymbolPrice/).

        Args:
            symbol: Symbol to retrieve price for.

        Returns:
            A coroutine which resolves when price MetatraderSymbolPrice is retrieved.
        """
        return self._websocketClient.get_symbol_price(self._account.id, symbol)

    @property
    def terminal_state(self) -> TerminalState:
        """Returns local copy of terminal state.

        Returns:
            Local copy of terminal state.
        """
        return self._terminalState

    @property
    def history_storage(self) -> HistoryStorage:
        """Returns local history storage.

        Returns:
            Local history storage.
        """
        return self._historyStorage

    def add_synchronization_listener(self, listener):
        """Adds synchronization listener.

        Args:
            listener: Synchronization listener to add.
        """
        self._websocketClient.add_synchronization_listener(self._account.id, listener)

    def remove_synchronization_listener(self, listener):
        """Removes synchronization listener for specific account.

        Args:
            listener: Synchronization listener to remove.
        """
        self._websocketClient.remove_synchronization_listener(self._account.id, listener)

    async def on_connected(self):
        """Invoked when connection to MetaTrader terminal established.

        Returns:
            A coroutine which resolves when the asynchronous event is processed.
        """
        try:
            await self.synchronize()
        except Exception as err:
            print(f'[{datetime.now().isoformat()}] MetaApi websocket client failed to synchronize', err)

    async def on_disconnected(self):
        """Invoked when connection to MetaTrader terminal terminated"""
        self._lastDisconnectedSynchronizationId = self._lastSynchronizationId
        self._lastSynchronizationId = None

    async def on_deal_synchronization_finished(self, synchronization_id: str):
        """Invoked when a synchronization of history deals on a MetaTrader account have finished.

        Args:
            synchronization_id: Synchronization request id.
        """
        self._dealsSynchronized[synchronization_id] = True
        await self._historyStorage.update_disk_storage()

    async def on_order_synchronization_finished(self, synchronization_id: str):
        """Invoked when a synchronization of history orders on a MetaTrader account have finished.

        Args:
            synchronization_id: Synchronization request id.
        """
        self._ordersSynchronized[synchronization_id] = True

    async def on_reconnected(self):
        """Invoked when connection to MetaApi websocket API restored after a disconnect.

        Returns:
            A coroutine which resolves when connection to MetaApi websocket API restored after a disconnect.
        """
        await self.subscribe()

    async def is_synchronized(self, synchronization_id: str = None) -> bool:
        """Returns flag indicating status of state synchronization with MetaTrader terminal.

        Args:
            synchronization_id: Optional synchronization request id, last synchronization request id will be used.

        Returns:
            A coroutine resolving with a flag indicating status of state synchronization with MetaTrader terminal.
        """
        synchronization_id = synchronization_id or self._lastSynchronizationId
        if synchronization_id in self._ordersSynchronized and self._ordersSynchronized[synchronization_id] \
                and synchronization_id in self._dealsSynchronized and self._dealsSynchronized[synchronization_id]:
            return True
        else:
            return False

    async def wait_synchronized(self, opts: SynchronizationOptions = None):
        """Waits until synchronization to MetaTrader terminal is completed.

        Args:
            opts: Synchronization options.

        Returns:
            A coroutine which resolves when synchronization to MetaTrader terminal is completed.

        Raises:
            TimeoutException: If application failed to synchronize with the terminal within timeout allowed.
        """
        start_time = datetime.now()
        opts = opts or {}
        synchronization_id = opts['synchronizationId'] if 'synchronizationId' in opts else None
        timeout_in_seconds = opts['timeoutInSeconds'] if 'timeoutInSeconds' in opts else 300
        interval_in_milliseconds = opts['intervalInMilliseconds'] if 'intervalInMilliseconds' in opts else 1000
        synchronized = await self.is_synchronized(synchronization_id)
        while not synchronized and (start_time + timedelta(seconds=timeout_in_seconds) > datetime.now()):
            await asyncio.sleep(interval_in_milliseconds / 1000)
            synchronized = await self.is_synchronized(synchronization_id)
        if not synchronized:
            raise TimeoutException('Timed out waiting for MetaApi to synchronize to MetaTrader account ' +
                                   self._account.id + ', synchronization id ' + (synchronization_id or
                                                                                 self._lastSynchronizationId or
                                                                                 self._lastDisconnectedSynchronizationId
                                                                                 or 'None'))
        time_left_in_seconds = max(0, timeout_in_seconds - (datetime.now() - start_time).total_seconds())
        await self._websocketClient.wait_synchronized(self._account.id, opts['applicationPattern'] if
                                                      'applicationPattern' in opts else '.*', time_left_in_seconds)

    def close(self):
        """Closes the connection. The instance of the class should no longer be used after this method is invoked."""
        if not self._closed:
            self._websocketClient.remove_synchronization_listener(self._account.id, self)
            self._websocketClient.remove_synchronization_listener(self._account.id, self._terminalState)
            self._websocketClient.remove_synchronization_listener(self._account.id, self._historyStorage)
            self._connection_registry.remove(self._account.id)
            self._closed = True