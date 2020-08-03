from .metaApiWebsocket_client import MetaApiWebsocketClient
from socketio import AsyncServer
from aiohttp import web
from ..models import date
import pytest
import asyncio
import copy
import re
from urllib.parse import parse_qs
from mock import MagicMock, AsyncMock, patch
sio = None
client = None


class FakeServer:

    def __init__(self):
        self.app = web.Application()
        self.runner = None

    async def start(self):
        port = 8080
        global sio
        sio = AsyncServer(async_mode='aiohttp')

        @sio.event
        async def connect(sid, environ):
            qs = parse_qs(environ['QUERY_STRING'])
            if ('auth-token' not in qs) or (qs['auth-token'] != ['token']):
                environ.emit({'error': 'UnauthorizedError', 'message': 'Authorization token invalid'})
                environ.close()

        sio.attach(self.app, socketio_path='ws')
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, 'localhost', port)
        await site.start()

    async def stop(self):
        await self.runner.cleanup()


@pytest.fixture(autouse=True)
async def run_around_tests():
    FinalMock.__await__ = lambda x: async_magic_close().__await__()
    fake_server = FakeServer()
    await fake_server.start()
    global client
    client = MetaApiWebsocketClient('token')
    client.set_url('http://localhost:8080')
    await client.connect()
    yield
    await client.close()
    await fake_server.stop()


# This method closes the client once the required socket event has been called
async def async_magic_close():
    await client.close()


class FinalMock(MagicMock):
    def __init__(self, *args, **kwargs):
        super(MagicMock, self).__init__(*args, **kwargs)


FinalMock.__await__ = lambda x: async_magic_close().__await__()


class TestMetaApiWebsocketClient:
    @pytest.mark.asyncio
    async def test_retrieve_account(self):
        """Should retrieve MetaTrader account information from API."""

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

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'getAccountInformation' and data['accountId'] == 'accountId':
                await sio.emit('response', {'type': 'response', 'accountId': data['accountId'],
                                            'requestId': data['requestId'], 'accountInformation': account_information})

        actual = await client.get_account_information('accountId')
        assert actual == account_information

    @pytest.mark.asyncio
    async def test_retrieve_positions(self):
        """Should retrieve MetaTrader positions from API."""

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

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'getPositions' and data['accountId'] == 'accountId':
                await sio.emit('response', {'type': 'response', 'accountId': data['accountId'],
                                            'requestId': data['requestId'], 'positions': positions})
            else:
                raise Exception('Wrong request')

        actual = await client.get_positions('accountId')
        assert actual == positions

    @pytest.mark.asyncio
    async def test_retrieve_position(self):
        """Should retrieve MetaTrader position from API."""

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

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'getPosition' and data['accountId'] == 'accountId' and data['positionId'] == '46214692':
                await sio.emit('response', {'type': 'response', 'accountId': data['accountId'],
                                            'requestId': data['requestId'], 'position': position})

        actual = await client.get_position('accountId', '46214692')
        assert actual == position

    @pytest.mark.asyncio
    async def test_retrieve_orders(self):
        """Should retrieve MetaTrader orders from API."""

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

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'getOrders' and data['accountId'] == 'accountId':
                await sio.emit('response', {'type': 'response', 'accountId': data['accountId'],
                                            'requestId': data['requestId'], 'orders': orders})

        actual = await client.get_orders('accountId')
        assert actual == orders

    @pytest.mark.asyncio
    async def test_retrieve_order(self):
        """Should retrieve MetaTrader order from API by id."""

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

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'getOrder' and data['accountId'] == 'accountId' and data['orderId'] == '46871284':
                await sio.emit('response', {'type': 'response', 'accountId': data['accountId'],
                                            'requestId': data['requestId'], 'order': order})

        actual = await client.get_order('accountId', '46871284')
        assert actual == order

    @pytest.mark.asyncio
    async def test_retrieve_history_orders_by_ticket(self):
        """Should retrieve MetaTrader history orders from API by ticket."""

        history_orders = [{
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
        }]

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'getHistoryOrdersByTicket' and data['accountId'] == 'accountId' and \
                    data['ticket'] == '46214692':
                await sio.emit('response', {'type': 'response', 'accountId': data['accountId'],
                                            'requestId': data['requestId'], 'historyOrders': history_orders,
                                            'synchronizing': False})

        actual = await client.get_history_orders_by_ticket('accountId', '46214692')
        assert actual == {'historyOrders': history_orders, 'synchronizing': False}

    @pytest.mark.asyncio
    async def test_retrieve_history_orders_by_position(self):
        """Should retrieve MetaTrader history orders from API by position."""

        history_orders = [{
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
        }]

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'getHistoryOrdersByPosition' and data['accountId'] == 'accountId' and \
                    data['positionId'] == '46214692':
                await sio.emit('response', {'type': 'response', 'accountId': data['accountId'],
                                            'requestId': data['requestId'], 'historyOrders': history_orders,
                                            'synchronizing': False})

        actual = await client.get_history_orders_by_position('accountId', '46214692')
        assert actual == {'historyOrders': history_orders, 'synchronizing': False}

    @pytest.mark.asyncio
    async def test_retrieve_history_orders_by_time_range(self):
        """Should retrieve MetaTrader history orders from API by time range."""

        history_orders = [{
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
        }]

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'getHistoryOrdersByTimeRange' and data['accountId'] == 'accountId' and \
                    data['startTime'] == '2020-04-15T02:45:00.000Z' and \
                    data['endTime'] == '2020-04-15T02:46:00.000Z' and data['offset'] == 1 and data['limit'] == 100:
                await sio.emit('response', {'type': 'response', 'accountId': data['accountId'],
                                            'requestId': data['requestId'], 'historyOrders': history_orders,
                                            'synchronizing': False})

        actual = await client.get_history_orders_by_time_range('accountId', date('2020-04-15T02:45:00.000Z'),
                                                               date('2020-04-15T02:46:00.000Z'), 1, 100)
        assert actual == {'historyOrders': history_orders, 'synchronizing': False}

    @pytest.mark.asyncio
    async def test_retrieve_deals_by_ticket(self):
        """Should retrieve MetaTrader deals from API by ticket."""

        deals = [{
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
        }]

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'getDealsByTicket' and data['accountId'] == 'accountId' and \
                    data['ticket'] == '46214692':
                await sio.emit('response', {'type': 'response', 'accountId': data['accountId'],
                                            'requestId': data['requestId'], 'deals': deals,
                                            'synchronizing': False})

        actual = await client.get_deals_by_ticket('accountId', '46214692')
        assert actual == {'deals': deals, 'synchronizing': False}

    @pytest.mark.asyncio
    async def test_retrieve_deals_by_position(self):
        """Should retrieve MetaTrader deals from API by position."""

        deals = [{
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
        }]

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'getDealsByPosition' and data['accountId'] == 'accountId' and \
                    data['positionId'] == '46214692':
                await sio.emit('response', {'type': 'response', 'accountId': data['accountId'],
                                            'requestId': data['requestId'], 'deals': deals,
                                            'synchronizing': False})

        actual = await client.get_deals_by_position('accountId', '46214692')
        assert actual == {'deals': deals, 'synchronizing': False}

    @pytest.mark.asyncio
    async def test_retrieve_deals_by_time_range(self):
        """Should retrieve MetaTrader deals from API by time range."""

        deals = [{
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
        }]

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'getDealsByTimeRange' and data['accountId'] == 'accountId' and \
                    data['startTime'] == '2020-04-15T02:45:00.000Z' and \
                    data['endTime'] == '2020-04-15T02:46:00.000Z' and data['offset'] == 1 and data['limit'] == 100:
                await sio.emit('response', {'type': 'response', 'accountId': data['accountId'],
                                            'requestId': data['requestId'], 'deals': deals,
                                            'synchronizing': False})

        actual = await client.get_deals_by_time_range('accountId', date('2020-04-15T02:45:00.000Z'),
                                                      date('2020-04-15T02:46:00.000Z'), 1, 100)
        assert actual == {'deals': deals, 'synchronizing': False}

    @pytest.mark.asyncio
    async def test_remove_history(self):
        """Should remove history from API."""

        request_received = False

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'removeHistory' and data['accountId'] == 'accountId':
                nonlocal request_received
                request_received = True
                await sio.emit('response', {'type': 'response', 'accountId': data['accountId'],
                                            'requestId': data['requestId']})

        await client.remove_history('accountId')
        assert request_received

    @pytest.mark.asyncio
    async def test_execute_trade(self):
        """Should execute a trade via API."""

        trade = {
            'actionType': 'ORDER_TYPE_SELL',
            'symbol': 'AUDNZD',
            'volume': 0.07
        }
        response = {
            'error': 10009,
            'description': 'TRADE_RETCODE_DONE',
            'orderId': '46870472'
        }

        @sio.on('request')
        async def on_request(sid, data):
            assert data['trade'] == trade
            if data['type'] == 'trade' and data['accountId'] == 'accountId':
                await sio.emit('response', {'type': 'response', 'accountId': data['accountId'],
                                            'requestId': data['requestId'], 'response': response})

        actual = await client.trade('accountId', trade)
        assert actual == response

    @pytest.mark.asyncio
    async def test_connect_to_terminal(self):
        """Should connect to MetaTrader terminal."""
        request_received = False

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'subscribe' and data['accountId'] == 'accountId':
                nonlocal request_received
                request_received = True

        await client.subscribe('accountId')
        await asyncio.sleep(0.05)
        assert request_received

    @pytest.mark.asyncio
    @patch('builtins.print', autospec=True, side_effect=print)
    async def test_return_error_if_failed(self, mock_print):
        """Should return error if connect to MetaTrader terminal failed."""
        request_received = False

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'subscribe' and data['accountId'] == 'accountId':
                nonlocal request_received
                request_received = True
            await sio.emit('processingError', {'id': 1, 'error': 'NotAuthenticatedError', 'message': 'Error message',
                                               'requestId': data['requestId']})

        await client.subscribe('accountId')
        await asyncio.sleep(0.05)
        re.match(r'MetaApi websocket client failed to receive subscribe response', mock_print.call_args_list[0].args[0])
        assert request_received

    @pytest.mark.asyncio
    async def test_reconnect_to_terminal(self):
        """Should reconnect to MetaTrader terminal."""

        request_received = False

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'reconnect' and data['accountId'] == 'accountId':
                nonlocal request_received
                request_received = True
                await sio.emit('response', {'type': 'response', 'accountId': data['accountId'],
                                            'requestId': data['requestId']})

        await client.reconnect('accountId')
        assert request_received

    @pytest.mark.asyncio
    async def test_retrieve_symbol_specification(self):
        """Should retrieve symbol specification from API."""

        specification = {
            'symbol': 'AUDNZD',
            'tickSize': 0.00001,
            'minVolume': 0.01,
            'maxVolume': 100,
            'volumeStep': 0.01
        }

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'getSymbolSpecification' and data['accountId'] == 'accountId' and \
                    data['symbol'] == 'AUDNZD':
                await sio.emit('response', {'type': 'response', 'accountId': data['accountId'],
                                            'requestId': data['requestId'], 'specification': specification})

        actual = await client.get_symbol_specification('accountId', 'AUDNZD')
        assert actual == specification

    @pytest.mark.asyncio
    async def test_retrieve_symbol_price(self):
        """Should retrieve symbol price from API."""

        price = {
            'symbol': 'AUDNZD',
            'bid': 1.05297,
            'ask': 1.05309,
            'profitTickValue': 0.59731,
            'lossTickValue': 0.59736
        }

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'getSymbolPrice' and data['accountId'] == 'accountId' and \
                    data['symbol'] == 'AUDNZD':
                await sio.emit('response', {'type': 'response', 'accountId': data['accountId'],
                                            'requestId': data['requestId'], 'price': price})

        actual = await client.get_symbol_price('accountId', 'AUDNZD')
        assert actual == price

    @pytest.mark.asyncio
    async def test_handle_validation_exception(self):
        """Should handle ValidationError."""

        trade = {
            'actionType': 'ORDER_TYPE_SELL',
            'symbol': 'AUDNZD'
        }

        @sio.on('request')
        async def on_request(sid, data):
            await sio.emit('processingError', {'id': 1, 'error': 'ValidationError', 'message': 'Validation failed',
                           'details': [{'parameter': 'volume', 'message': 'Required value.'}],
                                               'requestId': data['requestId']})

        try:
            await client.trade('accountId', trade)
            Exception('ValidationError expected')
        except Exception as err:
            assert err.__class__.__name__ == 'ValidationException'

    @pytest.mark.asyncio
    async def test_handle_not_found_exception(self):
        """Should handle NotFoundError."""

        @sio.on('request')
        async def on_request(sid, data):
            await sio.emit('processingError',  {'id': 1, 'error': 'NotFoundError',
                                                'message': 'Position id 1234 not found',
                                                'requestId': data['requestId']})

        try:
            await client.get_position('accountId', '1234')
            Exception('NotFoundException expected')
        except Exception as err:
            assert err.__class__.__name__ == 'NotFoundException'

    @pytest.mark.asyncio
    async def test_handle_not_synchronized_exception(self):
        """Should handle NotSynchronizedError."""

        @sio.on('request')
        async def on_request(sid, data):
            await sio.emit('processingError', {'id': 1, 'error': 'NotSynchronizedError', 'message': 'Error message',
                                               'requestId': data['requestId']})

        try:
            await client.get_position('accountId', '1234')
            Exception('NotSynchronizedError expected')
        except Exception as err:
            assert err.__class__.__name__ == 'NotSynchronizedException'

    @pytest.mark.asyncio
    async def test_handle_not_connected_exception(self):
        """Should handle NotSynchronizedError."""

        @sio.on('request')
        async def on_request(sid, data):
            await sio.emit('processingError', {'id': 1, 'error': 'NotAuthenticatedError', 'message': 'Error message',
                                               'requestId': data['requestId']})

        try:
            await client.get_position('accountId', '1234')
            Exception('NotConnectedError expected')
        except Exception as err:
            assert err.__class__.__name__ == 'NotConnectedException'

    @pytest.mark.asyncio
    async def test_handle_other_exceptions(self):
        """Should handle other errors."""

        @sio.on('request')
        async def on_request(sid, data):
            await sio.emit('processingError', {'id': 1, 'error': 'Error', 'message': 'Error message',
                                               'requestId': data['requestId']})

        try:
            await client.get_position('accountId', '1234')
            Exception('InternalError expected')
        except Exception as err:
            assert err.__class__.__name__ == 'InternalException'

    @pytest.mark.asyncio
    async def test_process_auth_sync_event(self):
        """Should process authenticated synchronization event."""
        listener = MagicMock()
        listener.on_connected = FinalMock()

        client.add_synchronization_listener('accountId', listener)
        await sio.emit('synchronization', {'type': 'authenticated', 'accountId': 'accountId'})
        await client._socket.wait()
        listener.on_connected.assert_called_with()

    @pytest.mark.asyncio
    async def test_process_broker_connection_status_event(self):
        """Should process broker connection status event."""
        listener = MagicMock()
        listener.on_broker_connection_status_changed = FinalMock()

        client.add_synchronization_listener('accountId', listener)
        await sio.emit('synchronization', {'type': 'status', 'accountId': 'accountId', 'connected': True})
        await client._socket.wait()
        listener.on_broker_connection_status_changed.assert_called_with(True)

    @pytest.mark.asyncio
    async def test_process_disconnected_synchronization_event(self):
        """Should process disconnected synchronization event."""

        listener = MagicMock()
        listener.on_disconnected = FinalMock()
        client.add_synchronization_listener('accountId', listener)
        await sio.emit('synchronization', {'type': 'disconnected', 'accountId': 'accountId'})
        await client._socket.wait()
        listener.on_disconnected.assert_called_with()

    @pytest.mark.asyncio
    async def test_synchronize_with_metatrader_terminal(self):
        """Should synchronize with MetaTrader terminal."""

        request_received = False

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'synchronize' and data['accountId'] == 'accountId' and \
                    data['startingHistoryOrderTime'] == '2020-01-01T00:00:00.000Z' and \
                    data['startingDealTime'] == '2020-01-02T00:00:00.000Z' and data['requestId'] == 'synchronizationId':
                nonlocal request_received
                request_received = True
                await sio.emit('response', {'type': 'response', 'accountId': data['accountId'],
                                            'requestId': data['requestId']})

        await client.synchronize('accountId', 'synchronizationId', date('2020-01-01T00:00:00.000Z'),
                                 date('2020-01-02T00:00:00.000Z'))
        assert request_received

    @pytest.mark.asyncio
    async def test_synchronize_account_information(self):
        """Should synchronize account information."""

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
        listener = MagicMock()
        listener.on_account_information_updated = FinalMock()

        client.add_synchronization_listener('accountId', listener)
        await sio.emit('synchronization', {'type': 'accountInformation', 'accountId': 'accountId',
                                           'accountInformation': account_information})
        await client._socket.wait()
        listener.on_account_information_updated.assert_called_with(account_information)

    @pytest.mark.asyncio
    async def test_synchronize_positions(self):
        """Should synchronize positions."""

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
        listener = MagicMock()
        listener.on_position_updated = FinalMock()

        client.add_synchronization_listener('accountId', listener)
        await sio.emit('synchronization', {'type': 'positions', 'accountId': 'accountId', 'positions': positions})
        await client._socket.wait()
        listener.on_position_updated.assert_called_with(positions[0])

    @pytest.mark.asyncio
    async def test_synchronize_orders(self):
        """Should synchronize orders."""

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
        listener = MagicMock()
        listener.on_order_updated = FinalMock()

        client.add_synchronization_listener('accountId', listener)
        await sio.emit('synchronization', {'type': 'orders', 'accountId': 'accountId', 'orders': orders})
        await client._socket.wait()
        listener.on_order_updated.assert_called_with(orders[0])

    @pytest.mark.asyncio
    async def test_synchronize_history_orders(self):
        """Should synchronize history orders."""

        history_orders = [{
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
        }]
        listener = MagicMock()
        listener.on_history_order_added = FinalMock()
        client.add_synchronization_listener('accountId', listener)
        await sio.emit('synchronization', {'type': 'historyOrders', 'accountId': 'accountId',
                                           'historyOrders': history_orders})
        await client._socket.wait()
        listener.on_history_order_added.assert_called_with(history_orders[0])

    @pytest.mark.asyncio
    async def test_synchronize_deals(self):
        """Should synchronize deals."""

        deals = [{
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
        }]
        listener = MagicMock()
        listener.on_deal_added = FinalMock()
        client.add_synchronization_listener('accountId', listener)
        await sio.emit('synchronization', {'type': 'deals', 'accountId': 'accountId', 'deals': deals})
        await client._socket.wait()
        listener.on_deal_added.assert_called_with(deals[0])

    @pytest.mark.asyncio
    async def test_process_synchronization_updates(self):
        """Should process synchronization updates."""

        update = {
            'accountInformation': {
                'broker': 'True ECN Trading Ltd',
                'currency': 'USD',
                'server': 'ICMarketsSC-Demo',
                'balance': 7319.9,
                'equity': 7306.649913200001,
                'margin': 184.1,
                'freeMargin': 7120.22,
                'leverage': 100,
                'marginLevel': 3967.58283542
            },
            'updatedPositions': [{
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
            }],
            'removedPositionIds': ['1234'],
            'updatedOrders': [{
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
            }],
            'completedOrderIds': ['2345'],
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
            }]
        }
        listener = MagicMock()
        listener.on_account_information_updated = AsyncMock()
        listener.on_position_updated = AsyncMock()
        listener.on_position_removed = AsyncMock()
        listener.on_order_updated = AsyncMock()
        listener.on_order_completed = AsyncMock()
        listener.on_history_order_added = AsyncMock()
        listener.on_deal_added = FinalMock()
        client.add_synchronization_listener('accountId', listener)
        emit = copy.deepcopy(update)
        emit['type'] = 'update'
        emit['accountId'] = 'accountId'
        await sio.emit('synchronization', emit)
        await client._socket.wait()
        listener.on_account_information_updated.assert_called_with(update['accountInformation'])
        listener.on_position_updated.assert_called_with(update['updatedPositions'][0])
        listener.on_position_removed.assert_called_with(update['removedPositionIds'][0])
        listener.on_order_updated.assert_called_with(update['updatedOrders'][0])
        listener.on_order_completed.assert_called_with(update['completedOrderIds'][0])
        listener.on_history_order_added.assert_called_with(update['historyOrders'][0])
        listener.on_deal_added.assert_called_with(update['deals'][0])

    @pytest.mark.asyncio
    async def test_timeout_on_no_response(self):
        """Should return timeout error if no server response received."""

        trade = {
            'actionType': 'ORDER_TYPE_SELL',
            'symbol': 'AUDNZD',
            'volume': 0.07
        }

        @sio.on('request')
        async def on_request(sid, data):
            pass

        try:
            await client.trade('accountId', trade)
            Exception('TimeoutError expected')
        except Exception as err:
            assert err.__class__.__name__ == 'TimeoutError'
            await client.close()

    @pytest.mark.asyncio
    async def test_subscribe_to_market_data_with_mt_terminal(self):
        """Should subscribe to market data with MetaTrader terminal."""

        request_received = False

        @sio.on('request')
        async def on_request(sid, data):
            if data['type'] == 'subscribeToMarketData' and data['accountId'] == 'accountId' and \
                    data['symbol'] == 'EURUSD':
                nonlocal request_received
                request_received = True
                await sio.emit('response', {'type': 'response', 'accountId': data['accountId'],
                                            'requestId': data['requestId']})

        await client.subscribe_to_market_data('accountId', 'EURUSD')
        assert request_received

    @pytest.mark.asyncio
    async def test_synchronize_symbol_specifications(self):
        """Should synchronize symbol specifications."""

        specifications = [{
            'symbol': 'EURUSD',
            'tickSize': 0.00001,
            'minVolume': 0.01,
            'maxVolume': 200,
            'volumeStep': 0.01
        }]
        listener = MagicMock()
        listener.on_symbol_specification_updated = FinalMock()
        client.add_synchronization_listener('accountId', listener)
        await sio.emit('synchronization', {'type': 'specifications', 'accountId': 'accountId',
                                           'specifications': specifications})
        await client._socket.wait()
        listener.on_symbol_specification_updated.assert_called_with(specifications[0])

    @pytest.mark.asyncio
    async def test_synchronize_symbol_prices(self):
        """Should synchronize symbol prices."""

        prices = [{
            'symbol': 'AUDNZD',
            'bid': 1.05916,
            'ask': 1.05927,
            'profitTickValue': 0.602,
            'lossTickValue': 0.60203
        }]
        listener = MagicMock()
        listener.on_symbol_price_updated = FinalMock()
        client.add_synchronization_listener('accountId', listener)
        await sio.emit('synchronization', {'type': 'prices', 'accountId': 'accountId', 'prices': prices})
        await client._socket.wait()
        listener.on_symbol_price_updated.assert_called_with(prices[0])
