from .clients.synchronizationListener import SynchronizationListener
from .models import MetatraderAccountInformation, MetatraderPosition, MetatraderOrder, \
    MetatraderSymbolSpecification, MetatraderSymbolPrice
import functools
from typing import List
import asyncio
from threading import Timer


class TerminalState(SynchronizationListener):
    """Responsible for storing a local copy of remote terminal state. Intended to be used with accounts which have user
    synchronization mode configured.
    """

    def __init__(self):
        """Inits the instance of terminal state class"""
        super().__init__()
        self._connected = False
        self._connectedToBroker = False
        self._accountInformation = None
        self._positions = []
        self._orders = []
        self._specifications = []
        self._specificationsBySymbol = {}
        self._pricesBySymbol = {}

    @property
    def connected(self) -> bool:
        """Returns true if MetaApi has connected to MetaTrader terminal.

        Returns:
            Whether MetaApi has connected to MetaTrader terminal.
        """
        return self._connected

    @property
    def connected_to_broker(self) -> bool:
        """Returns true if MetaApi has connected to MetaTrader terminal and MetaTrader terminal is connected to broker

        Returns:
             Whether MetaApi has connected to MetaTrader terminal and MetaTrader terminal is connected to broker
        """
        return self._connectedToBroker

    @property
    def account_information(self) -> MetatraderAccountInformation:
        """Returns a local copy of account information.

        Returns:
            Local copy of account information.
        """
        return self._accountInformation

    @property
    def positions(self) -> List[MetatraderPosition]:
        """Returns a local copy of MetaTrader positions opened.

        Returns:
            A local copy of MetaTrader positions opened.
        """
        return self._positions

    @property
    def orders(self) -> List[MetatraderOrder]:
        """Returns a local copy of MetaTrader orders opened.

        Returns:
            A local copy of MetaTrader orders opened.
        """
        return self._orders

    @property
    def specifications(self) -> List[MetatraderSymbolSpecification]:
        """Returns a local copy of symbol specifications available in MetaTrader trading terminal.

        Returns:
             A local copy of symbol specifications available in MetaTrader trading terminal.
        """
        return self._specifications

    def specification(self, symbol: str) -> MetatraderSymbolSpecification:
        """Returns MetaTrader symbol specification by symbol.

        Args:
            symbol: Symbol (e.g. currency pair or an index).

        Returns:
            MetatraderSymbolSpecification found or undefined if specification for a symbol is not found.
        """
        return self._specificationsBySymbol[symbol] if (symbol in self._specificationsBySymbol) else None

    def price(self, symbol: str) -> MetatraderSymbolPrice:
        """Returns MetaTrader symbol price by symbol.

        Args:
            symbol: Symbol (e.g. currency pair or an index).

        Returns:
            MetatraderSymbolPrice found or undefined if price for a symbol is not found.
        """
        return self._pricesBySymbol[symbol] if (symbol in self._pricesBySymbol) else None

    async def on_connected(self):
        """Invoked when connection to MetaTrader terminal established."""
        self._connected = True

    async def on_disconnected(self):
        """Invoked when connection to MetaTrader terminal terminated."""
        self._connected = False
        self._connectedToBroker = False

    async def on_broker_connection_status_changed(self, connected: bool):
        """Invoked when broker connection status have changed.

        Args:
            connected: Whether MetaTrader terminal is connected to broker.
        """
        def disconnect():
            asyncio.run(self.on_disconnected())
        self._connectedToBroker = connected
        if hasattr(self, '_status_timer'):
            self._status_timer.cancel()
        self._status_timer = Timer(60, disconnect)
        self._status_timer.start()

    async def on_account_information_updated(self, account_information: MetatraderAccountInformation):
        """Invoked when MetaTrader account information is updated.

        Args:
            account_information: Updated MetaTrader account information.
        """
        self._accountInformation = account_information

    async def on_position_updated(self, position: MetatraderPosition):
        """Invoked when MetaTrader position is updated.

        Args:
            position: Updated MetaTrader position.
        """
        for i in range(len(self._positions)):
            if self._positions[i]['id'] == position['id']:
                self._positions[i] = position
                break
        else:
            self._positions.append(position)

    async def on_position_removed(self, position_id: str):
        """Invoked when MetaTrader position is removed.

        Args:
            position_id: Removed MetaTrader position id.
        """
        self._positions = list(filter(lambda position: position['id'] != position_id, self._positions))

    async def on_order_updated(self, order: MetatraderOrder):
        """Invoked when MetaTrader order is updated

        Args:
            order: Updated MetaTrader order.
        """
        for i in range(len(self._orders)):
            if self._orders[i]['id'] == order['id']:
                self._orders[i] = order
                break
        else:
            self._orders.append(order)

    async def on_order_completed(self, order_id: str):
        """Invoked when MetaTrader order is completed (executed or canceled).

        Args:
            order_id: Completed MetaTrader order id.
        """
        self._orders = list(filter(lambda order: order['id'] != order_id, self._orders))

    async def on_symbol_specification_updated(self, specification: MetatraderSymbolSpecification):
        """Invoked when a symbol specification was updated.

        Args:
            specification: Updated MetaTrader symbol specification.
        """
        for i in range(len(self._specifications)):
            if self._specifications[i]['symbol'] == specification['symbol']:
                self._specifications[i] = specification
                break
        else:
            self._specifications.append(specification)
        self._specificationsBySymbol[specification['symbol']] = specification

    async def on_symbol_price_updated(self, price: MetatraderSymbolPrice):
        """Invoked when a symbol price was updated.

        Args:
            price: Updated MetaTrader symbol price.
        """
        self._pricesBySymbol[price['symbol']] = price
        positions = list(filter(lambda p: p['symbol'] == price['symbol'], self._positions))
        orders = list(filter(lambda o: o['symbol'] == price['symbol'], self._orders))
        specification = self.specification(price['symbol'])
        if specification:
            for position in positions:
                if 'unrealizedProfit' not in position or 'realizedProfit' not in position:
                    position['unrealizedProfit'] = (1 if (position['type'] == 'POSITION_TYPE_BUY') else -1) * \
                                                   (position['currentPrice'] - position['openPrice']) * \
                        position['currentTickValue'] * position['volume'] / specification['tickSize']
                    position['realizedProfit'] = position['profit'] - position['unrealizedProfit']
                new_position_price = price['bid'] if (position['type'] == 'POSITION_TYPE_BUY') else price['ask']
                is_profitable = (1 if (position['type'] == 'POSITION_TYPE_BUY') else -1) * (new_position_price -
                                                                                            position['openPrice'])
                current_tick_value = price['profitTickValue'] if (is_profitable > 0) else price['lossTickValue']
                unrealized_profit = (1 if (position['type'] == 'POSITION_TYPE_BUY') else -1) * \
                    (new_position_price - position['openPrice']) * current_tick_value * position['volume'] / \
                    specification['tickSize']
                increment = unrealized_profit - position['unrealizedProfit']
                position['unrealizedProfit'] = unrealized_profit
                position['profit'] = position['unrealizedProfit'] + position['realizedProfit']
                position['currentPrice'] = new_position_price
                position['currentTickValue'] = current_tick_value
                if self._accountInformation:
                    self._accountInformation['equity'] += increment
                    self._accountInformation['updateCount'] = (self._accountInformation['updateCount'] if
                                                               ('updateCount' in self._accountInformation) else 0) + 1
            for order in orders:
                order['currentPrice'] = price['ask'] if (order['type'] == 'ORDER_TYPE_BUY_LIMIT' or
                                                         order['type'] == 'ORDER_TYPE_BUY_STOP' or
                                                         order['type'] == 'ORDER_TYPE_BUY_STOP_LIMIT') else price['bid']
            if self._accountInformation and 'updateCount' in self._accountInformation and \
                    self._accountInformation['updateCount'] > 100:
                self._accountInformation['equity'] = self._accountInformation['balance'] + \
                                                     functools.reduce(lambda a, b: a + b['profit'], self._positions, 0)
                self._accountInformation['updateCount'] = 0
