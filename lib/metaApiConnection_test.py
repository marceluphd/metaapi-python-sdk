from .metaApiConnection import MetaApiConnection
from .clients.metaApiWebsocket_client import MetaApiWebsocketClient
from .models import MetatraderHistoryOrders, MetatraderDeals
from .clients.reconnectListener import ReconnectListener
from .clients.synchronizationListener import SynchronizationListener
from .metatraderAccount import MetatraderAccount
from datetime import datetime, timedelta
from mock import MagicMock, AsyncMock, patch
from .models import date, random_id
import pytest
import asyncio


class MockClient(MetaApiWebsocketClient):
    def get_account_information(self, account_id: str) -> asyncio.Future:
        pass

    def get_positions(self, account_id: str) -> asyncio.Future:
        pass

    def get_position(self, account_id: str, position_id: str) -> asyncio.Future:
        pass

    def get_orders(self, account_id: str) -> asyncio.Future:
        pass

    def get_order(self, account_id: str, order_id: str) -> asyncio.Future:
        pass

    def get_history_orders_by_ticket(self, account_id: str, ticket: str) -> MetatraderHistoryOrders:
        pass

    def get_history_orders_by_position(self, account_id: str, position_id: str) -> MetatraderHistoryOrders:
        pass

    def get_history_orders_by_time_range(self, account_id: str, start_time: datetime, end_time: datetime,
                                         offset=0, limit=1000) -> MetatraderHistoryOrders:
        pass

    def get_deals_by_ticket(self, account_id: str, ticket: str) -> MetatraderDeals:
        pass

    def get_deals_by_position(self, account_id: str, position_id: str) -> MetatraderDeals:
        pass

    def get_deals_by_time_range(self, account_id: str, start_time: datetime, end_time: datetime, offset: int = 0,
                                limit: int = 1000) -> MetatraderDeals:
        pass

    def remove_history(self, account_id: str):
        pass

    def trade(self, account_id: str, trade) -> asyncio.Future:
        pass

    def reconnect(self, account_id: str):
        pass

    def synchronize(self, account_id: str, starting_history_order_time: datetime, starting_deal_time: datetime):
        pass

    def subscribe(self, account_id: str):
        pass

    def subscribe_to_market_data(self, account_id: str, symbol: str):
        pass

    def add_synchronization_listener(self, account_id: str, listener):
        pass

    def add_reconnect_listener(self, listener: ReconnectListener):
        pass

    def remove_synchronization_listener(self, account_id: str, listener: SynchronizationListener):
        pass

    def get_symbol_specification(self, account_id: str, symbol: str) -> asyncio.Future:
        pass

    def get_symbol_price(self, account_id: str, symbol: str) -> asyncio.Future:
        pass


class MockAccount(MetatraderAccount):
    @property
    def id(self):
        return 'accountId'

    @property
    def synchronization_mode(self):
        return 'user'


class AutoMockAccount(MetatraderAccount):
    @property
    def id(self):
        return 'accountId'

    @property
    def synchronization_mode(self):
        return 'automatic'


account = MockAccount(MagicMock(), MagicMock(), MagicMock())
auto_account = AutoMockAccount(MagicMock(), MagicMock(), MagicMock())
client = MockClient('token')
api = MetaApiConnection(client, account)


@pytest.fixture(autouse=True)
async def run_around_tests():
    global api
    api = MetaApiConnection(client, account)
    yield


class TestMetaApiConnection:
    @pytest.mark.asyncio
    async def test_retrieve_account_information(self):
        """Should retrieve account information."""
        account_information = {
            'broker': 'True ECN Trading Ltd',
            'currency': 'USD',
            'server': 'ICMarketsSC-Demo',
            'balance': 7319.9,
            'equity': 7306.649913200001,
            'margin': 184.1,
            'freeMargin': 7120.22,
            'leverage': 100,
            'marginLevel': 3967.58283542
        }
        client.get_account_information = AsyncMock(return_value=account_information)
        actual = await api.get_account_information()
        assert actual == account_information
        client.get_account_information.assert_called_with('accountId')

    @pytest.mark.asyncio
    async def test_retrieve_positions(self):
        """Should retrieve positions."""
        positions = [{
            'id': '46214692',
            'type': 'POSITION_TYPE_BUY',
            'symbol': 'GBPUSD',
            'magic': 1000,
            'time': '2020-04-15T02:45:06.521Z',
            'updateTime': '2020-04-15T02:45:06.521Z',
            'openPrice': 1.26101,
            'currentPrice': 1.24883,
            'currentTickValue': 1,
            'volume': 0.07,
            'swap': 0,
            'profit': -85.25999999999966,
            'commission': -0.25,
            'clientId': 'TE_GBPUSD_7hyINWqAlE',
            'stopLoss': 1.17721,
            'unrealizedProfit': -85.25999999999901,
            'realizedProfit': -6.536993168992922e-13
        }]
        client.get_positions = AsyncMock(return_value=positions)
        actual = await api.get_positions()
        assert actual == positions
        client.get_positions.assert_called_with('accountId')

    @pytest.mark.asyncio
    async def test_retrieve_position_by_id(self):
        """Should retrieve position by id."""
        position = {
            'id': '46214692',
            'type': 'POSITION_TYPE_BUY',
            'symbol': 'GBPUSD',
            'magic': 1000,
            'time': '2020-04-15T02:45:06.521Z',
            'updateTime': '2020-04-15T02:45:06.521Z',
            'openPrice': 1.26101,
            'currentPrice': 1.24883,
            'currentTickValue': 1,
            'volume': 0.07,
            'swap': 0,
            'profit': -85.25999999999966,
            'commission': -0.25,
            'clientId': 'TE_GBPUSD_7hyINWqAlE',
            'stopLoss': 1.17721,
            'unrealizedProfit': -85.25999999999901,
            'realizedProfit': -6.536993168992922e-13
        }
        client.get_position = AsyncMock(return_value=position)
        actual = await api.get_position('46214692')
        assert actual == position
        client.get_position.assert_called_with('accountId', '46214692')

    @pytest.mark.asyncio
    async def test_retrieve_orders(self):
        """Should retrieve orders."""
        orders = [{
            'id': '46871284',
            'type': 'ORDER_TYPE_BUY_LIMIT',
            'state': 'ORDER_STATE_PLACED',
            'symbol': 'AUDNZD',
            'magic': 123456,
            'platform': 'mt5',
            'time': '2020-04-20T08:38:58.270Z',
            'openPrice': 1.03,
            'currentPrice': 1.05206,
            'volume': 0.01,
            'currentVolume': 0.01,
            'comment': 'COMMENT2'
        }]
        client.get_orders = AsyncMock(return_value=orders)
        actual = await api.get_orders()
        assert actual == orders
        client.get_orders.assert_called_with('accountId')

    @pytest.mark.asyncio
    async def test_retrieve_order_by_id(self):
        """Should retrieve order by id."""
        order = {
            'id': '46871284',
            'type': 'ORDER_TYPE_BUY_LIMIT',
            'state': 'ORDER_STATE_PLACED',
            'symbol': 'AUDNZD',
            'magic': 123456,
            'platform': 'mt5',
            'time': '2020-04-20T08:38:58.270Z',
            'openPrice': 1.03,
            'currentPrice': 1.05206,
            'volume': 0.01,
            'currentVolume': 0.01,
            'comment': 'COMMENT2'
        }
        client.get_order = AsyncMock(return_value=order)
        actual = await api.get_order('46871284')
        assert actual == order
        client.get_order.assert_called_with('accountId', '46871284')

    @pytest.mark.asyncio
    async def test_retrieve_history_orders_by_ticket(self):
        """Should retrieve history orders by ticket."""
        history_orders = {
            'historyOrders': [{
                'clientId': 'TE_GBPUSD_7hyINWqAlE',
                'currentPrice': 1.261,
                'currentVolume': 0,
                'doneTime': '2020-04-15T02:45:06.521Z',
                'id': '46214692',
                'magic': 1000,
                'platform': 'mt5',
                'positionId': '46214692',
                'state': 'ORDER_STATE_FILLED',
                'symbol': 'GBPUSD',
                'time': '2020-04-15T02:45:06.260Z',
                'type': 'ORDER_TYPE_BUY',
                'volume': 0.07
                }],
            'synchronizing': False
        }
        client.get_history_orders_by_ticket = AsyncMock(return_value=history_orders)
        actual = await api.get_history_orders_by_ticket('46214692')
        assert actual == history_orders
        client.get_history_orders_by_ticket.assert_called_with('accountId', '46214692')

    @pytest.mark.asyncio
    async def test_retrieve_history_orders_by_position(self):
        """Should retrieve history orders by position."""
        history_orders = {
            'historyOrders': [{
                'clientId': 'TE_GBPUSD_7hyINWqAlE',
                'currentPrice': 1.261,
                'currentVolume': 0,
                'doneTime': '2020-04-15T02:45:06.521Z',
                'id': '46214692',
                'magic': 1000,
                'platform': 'mt5',
                'positionId': '46214692',
                'state': 'ORDER_STATE_FILLED',
                'symbol': 'GBPUSD',
                'time': '2020-04-15T02:45:06.260Z',
                'type': 'ORDER_TYPE_BUY',
                'volume': 0.07
            }],
            'synchronizing': False
        }
        client.get_history_orders_by_position = AsyncMock(return_value=history_orders)
        actual = await api.get_history_orders_by_position('46214692')
        assert actual == history_orders
        client.get_history_orders_by_position.assert_called_with('accountId', '46214692')

    @pytest.mark.asyncio
    async def test_retrieve_history_orders_by_time_range(self):
        """Should retrieve history orders by time range."""
        history_orders = {
            'historyOrders': [{
                'clientId': 'TE_GBPUSD_7hyINWqAlE',
                'currentPrice': 1.261,
                'currentVolume': 0,
                'doneTime': '2020-04-15T02:45:06.521Z',
                'id': '46214692',
                'magic': 1000,
                'platform': 'mt5',
                'positionId': '46214692',
                'state': 'ORDER_STATE_FILLED',
                'symbol': 'GBPUSD',
                'time': '2020-04-15T02:45:06.260Z',
                'type': 'ORDER_TYPE_BUY',
                'volume': 0.07
            }],
            'synchronizing': False
        }
        client.get_history_orders_by_time_range = AsyncMock(return_value=history_orders)
        start_time = datetime.now() - timedelta(seconds=1)
        end_time = datetime.now()
        actual = await api.get_history_orders_by_time_range(start_time, end_time, 1, 100)
        assert actual == history_orders
        client.get_history_orders_by_time_range.assert_called_with('accountId', start_time, end_time, 1, 100)

    @pytest.mark.asyncio
    async def test_retrieve_history_deals_by_ticket(self):
        """Should retrieve history deals by ticket."""
        deals = {
            'deals': [{
                'clientId': 'TE_GBPUSD_7hyINWqAlE',
                'commission': -0.25,
                'entryType': 'DEAL_ENTRY_IN',
                'id': '33230099',
                'magic': 1000,
                'platform': 'mt5',
                'orderId': '46214692',
                'positionId': '46214692',
                'price': 1.26101,
                'profit': 0,
                'swap': 0,
                'symbol': 'GBPUSD',
                'time': '2020-04-15T02:45:06.521Z',
                'type': 'DEAL_TYPE_BUY',
                'volume': 0.07
            }],
            'synchronizing': False
        }
        client.get_deals_by_ticket = AsyncMock(return_value=deals)
        actual = await api.get_deals_by_ticket('46214692')
        assert actual == deals
        client.get_deals_by_ticket.assert_called_with('accountId', '46214692')

    @pytest.mark.asyncio
    async def test_retrieve_history_deals_by_position(self):
        """Should retrieve history deals by position."""
        deals = {
            'deals': [{
                'clientId': 'TE_GBPUSD_7hyINWqAlE',
                'commission': -0.25,
                'entryType': 'DEAL_ENTRY_IN',
                'id': '33230099',
                'magic': 1000,
                'platform': 'mt5',
                'orderId': '46214692',
                'positionId': '46214692',
                'price': 1.26101,
                'profit': 0,
                'swap': 0,
                'symbol': 'GBPUSD',
                'time': '2020-04-15T02:45:06.521Z',
                'type': 'DEAL_TYPE_BUY',
                'volume': 0.07
            }],
            'synchronizing': False
        }
        client.get_deals_by_position = AsyncMock(return_value=deals)
        actual = await api.get_deals_by_position('46214692')
        assert actual == deals
        client.get_deals_by_position.assert_called_with('accountId', '46214692')

    @pytest.mark.asyncio
    async def test_retrieve_history_deals_by_time_range(self):
        """Should retrieve history deals by time range."""
        deals = {
            'deals': [{
                'clientId': 'TE_GBPUSD_7hyINWqAlE',
                'commission': -0.25,
                'entryType': 'DEAL_ENTRY_IN',
                'id': '33230099',
                'magic': 1000,
                'platform': 'mt5',
                'orderId': '46214692',
                'positionId': '46214692',
                'price': 1.26101,
                'profit': 0,
                'swap': 0,
                'symbol': 'GBPUSD',
                'time': '2020-04-15T02:45:06.521Z',
                'type': 'DEAL_TYPE_BUY',
                'volume': 0.07
            }],
            'synchronizing': False
        }
        client.get_deals_by_time_range = AsyncMock(return_value=deals)
        start_time = datetime.now() - timedelta(seconds=1)
        end_time = datetime.now()
        actual = await api.get_deals_by_time_range(start_time, end_time, 1, 100)
        assert actual == deals
        client.get_deals_by_time_range.assert_called_with('accountId', start_time, end_time, 1, 100)

    @pytest.mark.asyncio
    async def test_remove_history(self):
        """Should remove history."""
        client.remove_history = AsyncMock()
        await api.remove_history()
        client.remove_history.assert_called_with('accountId')

    @pytest.mark.asyncio
    async def test_create_market_buy_order(self):
        """Should create market buy order."""
        trade_result = {
            'error': 10009,
            'description': 'TRADE_RETCODE_DONE',
            'orderId': 46870472
        }
        client.trade = AsyncMock(return_value=trade_result)
        actual = await api.create_market_buy_order('GBPUSD', 0.07, 0.9, 2.0, 'comment', 'TE_GBPUSD_7hyINWqAlE')
        assert actual == trade_result
        client.trade.assert_called_with('accountId', {'actionType': 'ORDER_TYPE_BUY', 'symbol': 'GBPUSD',
                                                      'volume': 0.07, 'stopLoss': 0.9, 'takeProfit': 2.0,
                                                      'comment': 'comment', 'clientId': 'TE_GBPUSD_7hyINWqAlE'})

    @pytest.mark.asyncio
    async def test_create_market_sell_order(self):
        """Should create market sell order."""
        trade_result = {
            'error': 10009,
            'description': 'TRADE_RETCODE_DONE',
            'orderId': 46870472
        }
        client.trade = AsyncMock(return_value=trade_result)
        actual = await api.create_market_sell_order('GBPUSD', 0.07, 0.9, 2.0, 'comment', 'TE_GBPUSD_7hyINWqAlE')
        assert actual == trade_result
        client.trade.assert_called_with('accountId', {'actionType': 'ORDER_TYPE_SELL', 'symbol': 'GBPUSD',
                                                      'volume': 0.07, 'stopLoss': 0.9, 'takeProfit': 2.0,
                                                      'comment': 'comment', 'clientId': 'TE_GBPUSD_7hyINWqAlE'})

    @pytest.mark.asyncio
    async def test_create_limit_buy_order(self):
        """Should create limit buy order."""
        trade_result = {
            'error': 10009,
            'description': 'TRADE_RETCODE_DONE',
            'orderId': 46870472
        }
        client.trade = AsyncMock(return_value=trade_result)
        actual = await api.create_limit_buy_order('GBPUSD', 0.07, 1.0, 0.9, 2.0, 'comment', 'TE_GBPUSD_7hyINWqAlE')
        assert actual == trade_result
        client.trade.assert_called_with('accountId', {'actionType': 'ORDER_TYPE_BUY_LIMIT', 'symbol': 'GBPUSD',
                                                      'volume': 0.07, 'openPrice': 1.0, 'stopLoss': 0.9,
                                                      'takeProfit': 2.0, 'comment': 'comment',
                                                      'clientId': 'TE_GBPUSD_7hyINWqAlE'})

    @pytest.mark.asyncio
    async def test_create_limit_sell_order(self):
        """Should create limit sell order."""
        trade_result = {
            'error': 10009,
            'description': 'TRADE_RETCODE_DONE',
            'orderId': 46870472
        }
        client.trade = AsyncMock(return_value=trade_result)
        actual = await api.create_limit_sell_order('GBPUSD', 0.07, 1.0, 0.9, 2.0, 'comment', 'TE_GBPUSD_7hyINWqAlE')
        assert actual == trade_result
        client.trade.assert_called_with('accountId', {'actionType': 'ORDER_TYPE_SELL_LIMIT', 'symbol': 'GBPUSD',
                                                      'volume': 0.07, 'openPrice': 1.0, 'stopLoss': 0.9,
                                                      'takeProfit': 2.0, 'comment': 'comment',
                                                      'clientId': 'TE_GBPUSD_7hyINWqAlE'})

    @pytest.mark.asyncio
    async def test_create_stop_buy_order(self):
        """Should create stop buy order."""
        trade_result = {
            'error': 10009,
            'description': 'TRADE_RETCODE_DONE',
            'orderId': 46870472
        }
        client.trade = AsyncMock(return_value=trade_result)
        actual = await api.create_stop_buy_order('GBPUSD', 0.07, 1.0, 0.9, 2.0, 'comment', 'TE_GBPUSD_7hyINWqAlE')
        assert actual == trade_result
        client.trade.assert_called_with('accountId', {'actionType': 'ORDER_TYPE_BUY_STOP', 'symbol': 'GBPUSD',
                                                      'volume': 0.07, 'openPrice': 1.0, 'stopLoss': 0.9,
                                                      'takeProfit': 2.0, 'comment': 'comment',
                                                      'clientId': 'TE_GBPUSD_7hyINWqAlE'})

    @pytest.mark.asyncio
    async def test_create_stop_sell_order(self):
        """Should create stop sell order."""
        trade_result = {
            'error': 10009,
            'description': 'TRADE_RETCODE_DONE',
            'orderId': 46870472
        }
        client.trade = AsyncMock(return_value=trade_result)
        actual = await api.create_stop_sell_order('GBPUSD', 0.07, 1.0, 0.9, 2.0, 'comment', 'TE_GBPUSD_7hyINWqAlE')
        assert actual == trade_result
        client.trade.assert_called_with('accountId', {'actionType': 'ORDER_TYPE_SELL_STOP', 'symbol': 'GBPUSD',
                                                      'volume': 0.07, 'openPrice': 1.0, 'stopLoss': 0.9,
                                                      'takeProfit': 2.0, 'comment': 'comment',
                                                      'clientId': 'TE_GBPUSD_7hyINWqAlE'})

    @pytest.mark.asyncio
    async def test_modify_position(self):
        """Should modify position."""
        trade_result = {
            'error': 10009,
            'description': 'TRADE_RETCODE_DONE',
            'orderId': 46870472
        }
        client.trade = AsyncMock(return_value=trade_result)
        actual = await api.modify_position('46870472', 2.0, 0.9)
        assert actual == trade_result
        client.trade.assert_called_with('accountId', {'actionType': 'POSITION_MODIFY', 'positionId': '46870472',
                                                      'stopLoss': 2.0, 'takeProfit': 0.9})

    @pytest.mark.asyncio
    async def test_close_position_partially(self):
        """Should close position partially."""
        trade_result = {
            'error': 10009,
            'description': 'TRADE_RETCODE_DONE',
            'orderId': 46870472
        }
        client.trade = AsyncMock(return_value=trade_result)
        actual = await api.close_position_partially('46870472', 0.9)
        assert actual == trade_result
        client.trade.assert_called_with('accountId', {'actionType': 'POSITION_PARTIAL', 'positionId': '46870472',
                                                      'volume': 0.9})

    @pytest.mark.asyncio
    async def test_close_position(self):
        """Should close position."""
        trade_result = {
            'error': 10009,
            'description': 'TRADE_RETCODE_DONE',
            'orderId': 46870472
        }
        client.trade = AsyncMock(return_value=trade_result)
        actual = await api.close_position('46870472')
        assert actual == trade_result
        client.trade.assert_called_with('accountId', {'actionType': 'POSITION_CLOSE_ID', 'positionId': '46870472'})

    @pytest.mark.asyncio
    async def test_close_position_by_symbol(self):
        """Should close position by symbol."""
        trade_result = {
            'error': 10009,
            'description': 'TRADE_RETCODE_DONE',
            'orderId': 46870472
        }
        client.trade = AsyncMock(return_value=trade_result)
        actual = await api.close_position_by_symbol('EURUSD')
        assert actual == trade_result
        client.trade.assert_called_with('accountId', {'actionType': 'POSITION_CLOSE_SYMBOL', 'symbol': 'EURUSD'})

    @pytest.mark.asyncio
    async def test_modify_order(self):
        """Should modify order."""
        trade_result = {
            'error': 10009,
            'description': 'TRADE_RETCODE_DONE',
            'orderId': 46870472
        }
        client.trade = AsyncMock(return_value=trade_result)
        actual = await api.modify_order('46870472', 1.0, 2.0, 0.9)
        assert actual == trade_result
        client.trade.assert_called_with('accountId', {'actionType': 'ORDER_MODIFY', 'orderId': '46870472',
                                                      'openPrice': 1.0, 'stopLoss': 2.0, 'takeProfit': 0.9})

    @pytest.mark.asyncio
    async def test_cancel_order(self):
        """Should cancel order."""
        trade_result = {
            'error': 10009,
            'description': 'TRADE_RETCODE_DONE',
            'orderId': 46870472
        }
        client.trade = AsyncMock(return_value=trade_result)
        actual = await api.cancel_order('46870472')
        assert actual == trade_result
        client.trade.assert_called_with('accountId', {'actionType': 'ORDER_CANCEL', 'orderId': '46870472'})

    @pytest.mark.asyncio
    async def test_reconnect_terminal(self):
        """Should reconnect terminal."""
        client.reconnect = AsyncMock()
        await api.reconnect()
        client.reconnect.assert_called_with('accountId')

    @pytest.mark.asyncio
    async def test_subscribe_to_terminal(self):
        """Should subscribe to terminal."""
        client.subscribe = AsyncMock()
        await api.subscribe()
        client.subscribe.assert_called_with('accountId')

    @pytest.mark.asyncio
    async def test_synchronize_state_with_terminal(self):
        """Should synchronize state with terminal."""
        client.synchronize = AsyncMock()
        with patch('lib.metaApiConnection.random_id', return_value='synchronizationId'):
            api = MetaApiConnection(client, account)
            await api.history_storage.on_history_order_added({'doneTime': date('2020-01-01T00:00:00.000Z')})
            await api.history_storage.on_deal_added({'time': date('2020-01-02T00:00:00.000Z')})
            await api.synchronize()
            client.synchronize.assert_called_with('accountId', 'synchronizationId', date('2020-01-01T00:00:00.000Z'),
                                                  date('2020-01-02T00:00:00.000Z'))

    @pytest.mark.asyncio
    async def test_subscribe_to_market_data(self):
        """Should subscribe to market data."""
        client.subscribe_to_market_data = AsyncMock()
        await api.subscribe_to_market_data('EURUSD')
        client.subscribe_to_market_data.assert_called_with('accountId', 'EURUSD')

    @pytest.mark.asyncio
    async def test_retrieve_symbol_specification(self):
        """Should retrieve symbol specification."""
        specification = {
            'symbol': 'AUDNZD',
            'tickSize': 0.00001,
            'minVolume': 0.01,
            'maxVolume': 100,
            'volumeStep': 0.01
        }
        client.get_symbol_specification = AsyncMock(return_value=specification)
        actual = await api.get_symbol_specification('AUDNZD')
        assert actual == specification
        client.get_symbol_specification.assert_called_with('accountId', 'AUDNZD')

    @pytest.mark.asyncio
    async def test_retrieve_symbol_price(self):
        """Should retrieve symbol price."""
        price = {
            'symbol': 'AUDNZD',
            'bid': 1.05297,
            'ask': 1.05309,
            'profitTickValue': 0.59731,
            'lossTickValue': 0.59736
        }
        client.get_symbol_price = AsyncMock(return_value=price)
        actual = await api.get_symbol_price('AUDNZD')
        assert actual == price

        client.get_symbol_price.assert_called_with('accountId', 'AUDNZD')

    @pytest.mark.asyncio
    async def test_initialize(self):
        """Should initialize listeners, terminal state and history storage for accounts with user sync mode."""
        client.add_synchronization_listener = MagicMock()
        api = MetaApiConnection(client, account)
        assert api.terminal_state
        assert api.history_storage
        client.add_synchronization_listener.assert_any_call('accountId', api)
        client.add_synchronization_listener.assert_any_call('accountId', api.terminal_state)
        client.add_synchronization_listener.assert_any_call('accountId', api.history_storage)

    @pytest.mark.asyncio
    async def test_add_sync_listeners(self):
        """Should add synchronization listeners for account with user synchronization mode."""
        client.add_synchronization_listener = MagicMock()
        api = MetaApiConnection(client, account)
        listener = {}
        api.add_synchronization_listener(listener)
        client.add_synchronization_listener.assert_called_with('accountId', listener)

    @pytest.mark.asyncio
    async def test_remove_sync_listeners(self):
        """Should remove synchronization listeners for account with user synchronization mode."""
        client.remove_synchronization_listener = MagicMock()
        api = MetaApiConnection(client, account)
        listener = {}
        api.remove_synchronization_listener(listener)
        client.remove_synchronization_listener.assert_called_with('accountId', listener)

    @pytest.mark.asyncio
    async def test_sync_on_connection(self):
        """Should synchronize on connection."""
        with patch('lib.metaApiConnection.random_id', return_value='synchronizationId'):
            client.synchronize = AsyncMock()
            api = MetaApiConnection(client, account)
            await api.history_storage.on_history_order_added({'doneTime': date('2020-01-01T00:00:00.000Z')})
            await api.history_storage.on_deal_added({'time': date('2020-01-02T00:00:00.000Z')})
            await api.on_connected()
            client.synchronize.assert_called_with('accountId', 'synchronizationId', date('2020-01-01T00:00:00.000Z'),
                                                  date('2020-01-02T00:00:00.000Z'))

    @pytest.mark.asyncio
    async def test_unsubscribe_from_events_on_close(self):
        """Should unsubscribe from events on close."""
        client.add_synchronization_listener = MagicMock()
        client.remove_synchronization_listener = MagicMock()
        api = MetaApiConnection(client, account)
        api.close()
        client.remove_synchronization_listener.assert_any_call('accountId', api)
        client.remove_synchronization_listener.assert_any_call('accountId', api.terminal_state)
        client.remove_synchronization_listener.assert_any_call('accountId', api.history_storage)

    @pytest.mark.timeout(60)
    @pytest.mark.asyncio
    async def test_wait_sync_complete_user_mode(self):
        """Should wait until synchronization complete in user mode."""
        assert not (await api.is_synchronized())
        try:
            await api.wait_synchronized('synchronizationId', 1, 10)
            raise Exception('TimeoutError is expected')
        except Exception as err:
            assert err.__class__.__name__ == 'TimeoutException'
        await api.on_order_synchronization_finished('synchronizationId')
        await api.on_deal_synchronization_finished('synchronizationId')
        promise = api.wait_synchronized('synchronizationId', 1, 10)
        start_time = datetime.now()
        await promise
        assert pytest.approx(0, 10) == (datetime.now() - start_time).seconds * 1000
        assert (await api.is_synchronized('synchronizationId'))

    @pytest.mark.asyncio
    async def test_time_out_waiting_for_sync_user_mode(self):
        """Should time out waiting for synchronization complete in user mode."""
        try:
            await api.wait_synchronized('synchronizationId', 1, 10)
            raise Exception('TimeoutError is expected')
        except Exception as err:
            assert err.__class__.__name__ == 'TimeoutException'
        assert not (await api.is_synchronized('synchronizationId'))

    @pytest.mark.asyncio
    async def test_wait_sync_complete_automatic_mode(self):
        """Should wait util synchronization complete in automatic mode."""
        api = MetaApiConnection(client, auto_account)
        client.get_deals_by_time_range = AsyncMock(side_effect=[{'synchronizing': True}, {'synchronizing': True},
                                                   {'synchronizing': True}, {'synchronizing': False},
                                                   {'synchronizing': False}, {'synchronizing': False}])
        assert not (await api.is_synchronized())
        start_time = datetime.now()
        await api.wait_synchronized('synchronizationId', 1, 10)
        assert pytest.approx(20, 10) == (datetime.now() - start_time).seconds * 1000
        assert (await api.is_synchronized('synchronizationId'))

    @pytest.mark.asyncio
    async def test_subscribe_to_terminal_on_reconnect(self):
        """Should subscribe to terminal on reconnect."""
        api.subscribe = AsyncMock()
        await api.on_reconnected()
        api.subscribe.assert_called_with()
