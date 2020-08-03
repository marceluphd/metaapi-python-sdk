from .clients.synchronizationListener import SynchronizationListener
from .clients.reconnectListener import ReconnectListener
from .clients.metaApiWebsocket_client import MetaApiWebsocketClient
from .terminalState import TerminalState
from .memoryHistoryStorage import MemoryHistoryStorage
from .metatraderAccountModel import MetatraderAccountModel
from .historyStorage import HistoryStorage
from .clients.timeoutException import TimeoutException
from .models import random_id
from datetime import datetime, timedelta
from typing import Coroutine
import asyncio


class MetaApiConnection(SynchronizationListener, ReconnectListener):
    """Exposes MetaApi MetaTrader API connection to consumers."""

    def __init__(self, websocket_client: MetaApiWebsocketClient, account: MetatraderAccountModel,
                 history_storage: HistoryStorage = None):
        """Inits MetaApi MetaTrader Api connection.

        Args:
            websocket_client: MetaApi websocket client.
            account: MetaTrader account id to connect to.
            history_storage: Local terminal history storage. Use for accounts in user synchronization mode. By default
            an instance of MemoryHistoryStorage will be used.
        """
        super().__init__()
        self._websocketClient = websocket_client
        self._account = account
        self._synchronized = False
        self._ordersSynchronized = {}
        self._dealsSynchronized = {}
        self._lastSynchronizationId = None
        if account.synchronization_mode == 'user':
            self._terminalState = TerminalState()
            self._historyStorage = history_storage or MemoryHistoryStorage()
            self._websocketClient.add_synchronization_listener(account.id, self)
            self._websocketClient.add_synchronization_listener(account.id, self._terminalState)
            self._websocketClient.add_synchronization_listener(account.id, self._historyStorage)
            self._websocketClient.add_reconnect_listener(self)

    def get_account_information(self) -> Coroutine:
        """Returns account information (see
        https://metaapi.cloud/docs/client/websocket/api/readTradingTerminalState/readAccountInformation/).

        Returns:
            A coroutine resolving with account information.
        """
        return self._websocketClient.get_account_information(self._account.id)

    def get_positions(self) -> Coroutine:
        """Returns positions (see
        https://metaapi.cloud/docs/client/websocket/api/readTradingTerminalState/readPositions/).

        Returns:
            A coroutine resolving with array of open positions.
        """
        return self._websocketClient.get_positions(self._account.id)

    def get_position(self, position_id: str) -> Coroutine:
        """Returns specific position (see
        https://metaapi.cloud/docs/client/websocket/api/readTradingTerminalState/readPosition/).

        Args:
            position_id: Position id.

        Returns:
            A coroutine resolving with MetaTrader position found.
        """
        return self._websocketClient.get_position(self._account.id, position_id)

    def get_orders(self) -> Coroutine:
        """Returns open orders (see
        https://metaapi.cloud/docs/client/websocket/api/readTradingTerminalState/readOrders/).

        Returns:
            A coroutine resolving with open MetaTrader orders.
        """
        return self._websocketClient.get_orders(self._account.id)

    def get_order(self, order_id: str) -> Coroutine:
        """Returns specific open order (see
        https://metaapi.cloud/docs/client/websocket/api/readTradingTerminalState/readOrder/).

        Args:
            order_id: Order id (ticket number).

        Returns:
            A coroutine resolving with metatrader order found.
        """
        return self._websocketClient.get_order(self._account.id, order_id)

    def get_history_orders_by_ticket(self, ticket: str) -> Coroutine:
        """Returns the history of completed orders for a specific ticket number (see
        https://metaapi.cloud/docs/client/websocket/api/retrieveHistoricalData/readHistoryOrdersByTicket/).

        Args:
            ticket: Ticket number (order id).

        Returns:
            A coroutine resolving with request results containing history orders found.
        """
        return self._websocketClient.get_history_orders_by_ticket(self._account.id, ticket)

    def get_history_orders_by_position(self, position_id: str) -> Coroutine:
        """Returns the history of completed orders for a specific position id (see
        https://metaapi.cloud/docs/client/websocket/api/retrieveHistoricalData/readHistoryOrdersByPosition/)

        Args:
            position_id: Position id.

        Returns:
            A coroutine resolving with request results containing history orders found.
        """
        return self._websocketClient.get_history_orders_by_position(self._account.id, position_id)

    def get_history_orders_by_time_range(self, start_time: datetime, end_time: datetime, offset: int = 0,
                                         limit: int = 1000) -> Coroutine:
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

    def get_deals_by_ticket(self, ticket: str) -> Coroutine:
        """Returns history deals with a specific ticket number (see
        https://metaapi.cloud/docs/client/websocket/api/retrieveHistoricalData/readDealsByTicket/).

        Args:
            ticket: Ticket number (deal id for MT5 or order id for MT4).

        Returns:
            A coroutine resolving with request results containing deals found.
        """
        return self._websocketClient.get_deals_by_ticket(self._account.id, ticket)

    def get_deals_by_position(self, position_id) -> Coroutine:
        """Returns history deals for a specific position id (see
        https://metaapi.cloud/docs/client/websocket/api/retrieveHistoricalData/readDealsByPosition/).

        Args:
            position_id: Position id.

        Returns:
            A coroutine resolving with request results containing deals found.
        """
        return self._websocketClient.get_deals_by_position(self._account.id, position_id)

    def get_deals_by_time_range(self, start_time: datetime, end_time: datetime, offset: int = 0,
                                limit: int = 1000) -> Coroutine:
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
        return self._websocketClient.remove_history(self._account.id)

    def create_market_buy_order(self, symbol: str, volume: float, stop_loss: float = None, take_profit: float = None,
                                comment: str = None, client_id: str = None) -> Coroutine:
        """Creates a market buy order (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            symbol: Symbol to trade.
            volume: Order volume.
            stop_loss: Optional stop loss price.
            take_profit: Optional take profit price.
            comment: Optional order comment. The sum of the line lengths of the comment and the clientId must
            be less than or equal to 27. For more information see https://metaapi.cloud/docs/client/clientIdUsage/
            client_id: optional client-assigned id. The id value can be assigned when submitting a trade and will be
            present on position, history orders and history deals related to the trade. You can use this field to bind
            your trades to objects in your application and then track trade progress. The sum of the line lengths of
            the comment and the clientId must be less than or equal to 27. For more information
            see https://metaapi.cloud/docs/client/clientIdUsage/

        Returns:
            A coroutine resolving with trade result.
        """
        trade_params = {'actionType': 'ORDER_TYPE_BUY', 'symbol': symbol, 'volume': volume}
        if stop_loss:
            trade_params['stopLoss'] = stop_loss
        if take_profit:
            trade_params['takeProfit'] = take_profit
        if comment:
            trade_params['comment'] = comment
        if client_id:
            trade_params['clientId'] = client_id
        return self._websocketClient.trade(self._account.id, trade_params)

    def create_market_sell_order(self, symbol: str, volume: float, stop_loss: float = None, take_profit: float = None,
                                 comment: str = None, client_id: str = None) -> Coroutine:
        """Creates a market sell order (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            symbol: Symbol to trade.
            volume: Order volume.
            stop_loss: Optional stop loss price.
            take_profit: Optional take profit price.
            comment: Optional order comment. The sum of the line lengths of the comment and the clientId must
            be less than or equal to 27. For more information see https://metaapi.cloud/docs/client/clientIdUsage/
            client_id: optional client-assigned id. The id value can be assigned when submitting a trade and will be
            present on position, history orders and history deals related to the trade. You can use this field to bind
            your trades to objects in your application and then track trade progress. The sum of the line lengths of
            the comment and the clientId must be less than or equal to 27. For more information
            see https://metaapi.cloud/docs/client/clientIdUsage/

        Returns:
            A coroutine resolving with trade result.
        """
        trade_params = {'actionType': 'ORDER_TYPE_SELL', 'symbol': symbol, 'volume': volume}
        if stop_loss:
            trade_params['stopLoss'] = stop_loss
        if take_profit:
            trade_params['takeProfit'] = take_profit
        if comment:
            trade_params['comment'] = comment
        if client_id:
            trade_params['clientId'] = client_id
        return self._websocketClient.trade(self._account.id, trade_params)

    def create_limit_buy_order(self, symbol: str, volume: float, open_price: float, stop_loss: float = None,
                               take_profit: float = None, comment: str = None, client_id: str = None) -> Coroutine:
        """Creates a limit buy order (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            symbol: Symbol to trade.
            volume: Order volume.
            open_price: Order limit price.
            stop_loss: Optional stop loss price.
            take_profit: Optional take profit price.
            comment: Optional order comment. The sum of the line lengths of the comment and the clientId must
            be less than or equal to 27. For more information see https://metaapi.cloud/docs/client/clientIdUsage/
            client_id: optional client-assigned id. The id value can be assigned when submitting a trade and will be
            present on position, history orders and history deals related to the trade. You can use this field to bind
            your trades to objects in your application and then track trade progress. The sum of the line lengths of
            the comment and the clientId must be less than or equal to 27. For more information
            see https://metaapi.cloud/docs/client/clientIdUsage/

        Returns:
            A coroutine resolving with trade result.
        """
        trade_params = {'actionType': 'ORDER_TYPE_BUY_LIMIT', 'symbol': symbol, 'volume': volume,
                        'openPrice': open_price}
        if stop_loss:
            trade_params['stopLoss'] = stop_loss
        if take_profit:
            trade_params['takeProfit'] = take_profit
        if comment:
            trade_params['comment'] = comment
        if client_id:
            trade_params['clientId'] = client_id
        return self._websocketClient.trade(self._account.id, trade_params)

    def create_limit_sell_order(self, symbol: str, volume: float, open_price: float, stop_loss: float = None,
                                take_profit: float = None, comment: str = None, client_id: str = None) -> Coroutine:
        """Creates a limit sell order (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            symbol: Symbol to trade.
            volume: Order volume.
            open_price: Order limit price.
            stop_loss: Optional stop loss price.
            take_profit: Optional take profit price.
            comment: Optional order comment. The sum of the line lengths of the comment and the clientId must
            be less than or equal to 27. For more information see https://metaapi.cloud/docs/client/clientIdUsage/
            client_id: optional client-assigned id. The id value can be assigned when submitting a trade and will be
            present on position, history orders and history deals related to the trade. You can use this field to bind
            your trades to objects in your application and then track trade progress. The sum of the line lengths of
            the comment and the clientId must be less than or equal to 27. For more information
            see https://metaapi.cloud/docs/client/clientIdUsage/

        Returns:
            A coroutine resolving with trade result.
        """
        trade_params = {'actionType': 'ORDER_TYPE_SELL_LIMIT', 'symbol': symbol, 'volume': volume,
                        'openPrice': open_price}
        if stop_loss:
            trade_params['stopLoss'] = stop_loss
        if take_profit:
            trade_params['takeProfit'] = take_profit
        if comment:
            trade_params['comment'] = comment
        if client_id:
            trade_params['clientId'] = client_id
        return self._websocketClient.trade(self._account.id, trade_params)

    def create_stop_buy_order(self, symbol: str, volume: float, open_price: float, stop_loss: float = None,
                              take_profit: float = None, comment: str = None, client_id: str = None) -> Coroutine:
        """Creates a stop buy order (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            symbol: Symbol to trade.
            volume: Order volume.
            open_price: Order limit price.
            stop_loss: Optional stop loss price.
            take_profit: Optional take profit price.
            comment: Optional order comment. The sum of the line lengths of the comment and the clientId must
            be less than or equal to 27. For more information see https://metaapi.cloud/docs/client/clientIdUsage/
            client_id: optional client-assigned id. The id value can be assigned when submitting a trade and will be
            present on position, history orders and history deals related to the trade. You can use this field to bind
            your trades to objects in your application and then track trade progress. The sum of the line lengths of
            the comment and the clientId must be less than or equal to 27. For more information
            see https://metaapi.cloud/docs/client/clientIdUsage/

        Returns:
            A coroutine resolving with trade result.
        """
        trade_params = {'actionType': 'ORDER_TYPE_BUY_STOP', 'symbol': symbol, 'volume': volume,
                        'openPrice': open_price}
        if stop_loss:
            trade_params['stopLoss'] = stop_loss
        if take_profit:
            trade_params['takeProfit'] = take_profit
        if comment:
            trade_params['comment'] = comment
        if client_id:
            trade_params['clientId'] = client_id
        return self._websocketClient.trade(self._account.id, trade_params)

    def create_stop_sell_order(self, symbol: str, volume: float, open_price: float, stop_loss: float = None,
                               take_profit: float = None, comment: str = None, client_id: str = None) -> Coroutine:
        """Creates a stop sell order (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            symbol: Symbol to trade.
            volume: Order volume.
            open_price: Order limit price.
            stop_loss: Optional stop loss price.
            take_profit: Optional take profit price.
            comment: Optional order comment. The sum of the line lengths of the comment and the clientId must
            be less than or equal to 27. For more information see https://metaapi.cloud/docs/client/clientIdUsage/
            client_id: optional client-assigned id. The id value can be assigned when submitting a trade and will be
            present on position, history orders and history deals related to the trade. You can use this field to bind
            your trades to objects in your application and then track trade progress. The sum of the line lengths of
            the comment and the clientId must be less than or equal to 27. For more information
            see https://metaapi.cloud/docs/client/clientIdUsage/

        Returns:
            A coroutine resolving with trade result.
        """
        trade_params = {'actionType': 'ORDER_TYPE_SELL_STOP', 'symbol': symbol, 'volume': volume,
                        'openPrice': open_price}
        if stop_loss:
            trade_params['stopLoss'] = stop_loss
        if take_profit:
            trade_params['takeProfit'] = take_profit
        if comment:
            trade_params['comment'] = comment
        if client_id:
            trade_params['clientId'] = client_id
        return self._websocketClient.trade(self._account.id, trade_params)

    def modify_position(self, position_id: str, stop_loss: float = None, take_profit: float = None) -> Coroutine:
        """Modifies a position (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            position_id: Position id to modify.
            stop_loss: Optional stop loss price.
            take_profit: Optional take profit price.

        Returns:
            A coroutine resolving with trade result.
        """
        trade_params = {'actionType': 'POSITION_MODIFY', 'positionId': position_id}
        if stop_loss:
            trade_params['stopLoss'] = stop_loss
        if take_profit:
            trade_params['takeProfit'] = take_profit
        return self._websocketClient.trade(self._account.id, trade_params)

    def close_position_partially(self, position_id: str, volume: float, comment: str = None, client_id: str = None) \
            -> Coroutine:
        """Partially closes a position (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            position_id: Position id to modify.
            volume: Volume to close.
            comment: Optional order comment. The sum of the line lengths of the comment and the clientId must be less
            than or equal to 27. For more information see https://metaapi.cloud/docs/client/clientIdUsage/.
            client_id: Optional client-assigned id. The id value can be assigned when submitting a trade and will be
            present on position, history orders and history deals related to the trade. You can use this field to bind
            your trades to objects in your application and then track trade progress. The sum of the line lengths of
            the comment and the clientId must be less than or equal to 27. For more information
            see https://metaapi.cloud/docs/client/clientIdUsage/

        Returns:
            A coroutine resolving with trade result.
        """
        trade_params = {'actionType': 'POSITION_PARTIAL', 'positionId': position_id, 'volume': volume}
        if comment:
            trade_params['comment'] = comment
        if client_id:
            trade_params['clientId'] = client_id
        return self._websocketClient.trade(self._account.id, trade_params)

    def close_position(self, position_id: str, comment: str = None, client_id: str = None) -> Coroutine:
        """Fully closes a position (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            position_id: Position id to modify.
            comment: Optional order comment. The sum of the line lengths of the comment and the clientId must be less
            than or equal to 27. For more information see https://metaapi.cloud/docs/client/clientIdUsage/.
            client_id: Optional client-assigned id. The id value can be assigned when submitting a trade and will be
            present on position, history orders and history deals related to the trade. You can use this field to bind
            your trades to objects in your application and then track trade progress. The sum of the line lengths of
            the comment and the clientId must be less than or equal to 27. For more information
            see https://metaapi.cloud/docs/client/clientIdUsage/

        Returns:
            A coroutine resolving with trade result.
        """
        trade_params = {'actionType': 'POSITION_CLOSE_ID', 'positionId': position_id}
        if comment:
            trade_params['comment'] = comment
        if client_id:
            trade_params['clientId'] = client_id
        return self._websocketClient.trade(self._account.id, trade_params)

    def close_position_by_symbol(self, symbol: str, comment: str = None, client_id: str = None) -> Coroutine:
        """Closes position by a symbol. Available on MT5 netting accounts only. (see
        https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            symbol: Symbol to trade.
            comment: optional order comment. The sum of the line lengths of the comment and the clientId
            must be less than or equal to 27. For more information see https://metaapi.cloud/docs/client/clientIdUsage/
            client_id: Optional client-assigned id. The id value can be assigned when submitting a trade and will be
            present on position, history orders and history deals related to the trade. You can use this field to bind
            your trades to objects in your application and then track trade progress. The sum of the line lengths of
            the comment and the clientId must be less than or equal to 27. For more information
            see https://metaapi.cloud/docs/client/clientIdUsage/

        Returns:
            A coroutine resolving with trade result.
        """
        trade_params = {'actionType': 'POSITION_CLOSE_SYMBOL', 'symbol': symbol}
        if comment:
            trade_params['comment'] = comment
        if client_id:
            trade_params['clientId'] = client_id
        return self._websocketClient.trade(self._account.id, trade_params)

    def modify_order(self, order_id: str, open_price: float, stop_loss: float = None,
                     take_profit: float = None) -> Coroutine:
        """Modifies a pending order (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            order_id: Order id (ticket number).
            open_price: Order stop price.
            stop_loss: Optional stop loss price.
            take_profit: Optional take profit price.

        Returns:
            A coroutine resolving with trade result.
        """
        trade_params = {'actionType': 'ORDER_MODIFY', 'orderId': order_id, 'openPrice': open_price}
        if stop_loss:
            trade_params['stopLoss'] = stop_loss
        if take_profit:
            trade_params['takeProfit'] = take_profit
        return self._websocketClient.trade(self._account.id, trade_params)

    def cancel_order(self, order_id: str) -> Coroutine:
        """Cancels order (see https://metaapi.cloud/docs/client/websocket/api/trade/).

        Args:
            order_id: Order id (ticket number).

        Returns:
            A coroutine resolving with trade result.
        """
        return self._websocketClient.trade(self._account.id, {'actionType': 'ORDER_CANCEL', 'orderId': order_id})

    def reconnect(self) -> Coroutine:
        """Reconnects to the Metatrader terminal (see https://metaapi.cloud/docs/client/websocket/api/reconnect/).

        Returns:
            A coroutine which resolves when reconnection started.
        """
        return self._websocketClient.reconnect(self._account.id)

    async def synchronize(self) -> Coroutine:
        """Requests the terminal to start synchronization process. Use it if user synchronization mode is set to user
        for the account (see https://metaapi.cloud/docs/client/websocket/synchronizing/synchronize/). Use only for user
        synchronization mode.

        Returns:
            A coroutine which resolves when synchronization started.
        """
        if self._account.synchronization_mode == 'user':
            starting_history_order_time = await self._historyStorage.last_history_order_time()
            starting_deal_time = await self._historyStorage.last_deal_time()
            synchronization_id = random_id()
            self._lastSynchronizationId = synchronization_id
            return await self._websocketClient.synchronize(self._account.id, synchronization_id,
                                                           starting_history_order_time, starting_deal_time)

    async def subscribe(self) -> Coroutine:
        """Initiates subscription to MetaTrader terminal.

        Returns:
            A coroutine which resolves when subscription is initiated.
        """
        return await self._websocketClient.subscribe(self._account.id)

    def subscribe_to_market_data(self, symbol: str) -> Coroutine:
        """Subscribes on market data of specified symbol (see
        https://metaapi.cloud/docs/client/websocket/marketDataStreaming/subscribeToMarketData/).

        Args:
            symbol: Symbol (e.g. currency pair or an index).

        Returns:
            Promise which resolves when subscription request was processed.
        """
        return self._websocketClient.subscribe_to_market_data(self._account.id, symbol)

    def get_symbol_specification(self, symbol: str) -> Coroutine:
        """Retrieves specification for a symbol (see
        https://metaapi.cloud/docs/client/websocket/api/retrieveMarketData/getSymbolSpecification/).

        Args:
            symbol: Symbol to retrieve specification for.

        Returns:
            A coroutine which resolves when specification is retrieved.
        """
        return self._websocketClient.get_symbol_specification(self._account.id, symbol)

    def get_symbol_price(self, symbol) -> Coroutine:
        """Retrieves specification for a symbol (see
        https://metaapi.cloud/docs/client/websocket/api/retrieveMarketData/getSymbolPrice/).

        Args:
            symbol: Symbol to retrieve price for.

        Returns:
            A coroutine which resolves when price is retrieved.
        """
        return self._websocketClient.get_symbol_price(self._account.id, symbol)

    @property
    def terminal_state(self) -> TerminalState:
        """Returns local copy of terminal state. Use this method for accounts in user synchronization mode.

        Returns:
            Local copy of terminal state.
        """
        return self._terminalState

    @property
    def history_storage(self) -> HistoryStorage:
        """Returns local history storage. Use this method for accounts in user synchronization mode.

        Returns:
            Local history storage.
        """
        return self._historyStorage

    def add_synchronization_listener(self, listener):
        """Adds synchronization listener. Use this method for accounts in user synchronization mode.

        Args:
            listener: Synchronization listener to add.
        """
        if self._account.synchronization_mode == 'user':
            self._websocketClient.add_synchronization_listener(self._account.id, listener)

    def remove_synchronization_listener(self, listener):
        """Removes synchronization listener for specific account. Use this method for accounts in user
        synchronization mode.

        Args:
            listener: Synchronization listener to remove.
        """
        if self._account.synchronization_mode == 'user':
            self._websocketClient.remove_synchronization_listener(self._account.id, listener)

    async def on_connected(self):
        """Invoked when connection to MetaTrader terminal established.

        Returns:
            A coroutine which resolves when the asynchronous event is processed.
        """
        await self.synchronize()

    async def on_disconnected(self):
        """Invoked when connection to MetaTrader terminal terminated"""
        self._lastSynchronizationId = None

    async def on_deal_synchronization_finished(self, synchronization_id: str):
        """Invoked when a synchronization of history deals on a MetaTrader account have finished

        Args:
            synchronization_id: Synchronization request id.
        """
        self._dealsSynchronized[synchronization_id] = True

    async def on_order_synchronization_finished(self, synchronization_id: str):
        """Invoked when a synchronization of history orders on a MetaTrader account have finished

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
        if self._account.synchronization_mode == 'user':
            return synchronization_id in self._ordersSynchronized and self._ordersSynchronized[synchronization_id] \
                and synchronization_id in self._dealsSynchronized and self._dealsSynchronized[synchronization_id]
        else:
            result = await self.get_deals_by_time_range(datetime.utcnow(), datetime.utcnow())
            return not result['synchronizing']

    async def wait_synchronized(self, synchronization_id: str = None, timeout_in_seconds: int = 300,
                                interval_in_milliseconds: int = 1000):
        """Waits until synchronization to MetaTrader terminal is completed.

        Args:
            synchronization_id: Optional synchronization id, last synchronization request id will be used by default.
            timeout_in_seconds: Wait timeout in seconds, default is 5m.
            interval_in_milliseconds: Interval between account reloads while waiting for a change, default is 1s.

        Returns:
            A coroutine which resolves when synchronization to MetaTrader terminal is completed.

        Raises:
            TimeoutException: If application failed to synchronize with the terminal within timeout allowed.
        """
        start_time = datetime.now()
        while not(await self.is_synchronized(synchronization_id)) \
                and (start_time + timedelta(seconds=timeout_in_seconds) > datetime.now()):
            await asyncio.sleep(interval_in_milliseconds / 1000)
        if not(await self.is_synchronized(synchronization_id)):
            raise TimeoutException('Timed out waiting for MetaApi to synchronize to MetaTrader account ' +
                                   self._account.id + ', synchronization id ' + (synchronization_id or 'None'))

    def close(self):
        """Closes the connection. The instance of the class should no longer be used after this method is invoked."""
        if self._account.synchronization_mode == 'user':
            self._websocketClient.remove_synchronization_listener(self._account.id, self)
            self._websocketClient.remove_synchronization_listener(self._account.id, self._terminalState)
            self._websocketClient.remove_synchronization_listener(self._account.id, self._historyStorage)
