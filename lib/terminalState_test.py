from lib.terminalState import TerminalState
import pytest
state = TerminalState()


@pytest.fixture(autouse=True)
def run_around_tests():
    global state
    state = TerminalState()
    yield


class TestTerminalState:
    def test_return_connection_state(self):
        """Should return connection state."""
        assert not state.connected
        state.on_connected()
        assert state.connected
        state.on_disconnected()
        assert not state.connected

    def test_return_broker_connection_state(self):
        """Should return broker connection state."""
        assert not state.connected_to_broker
        state.on_broker_connection_status_changed(True)
        assert state.connected_to_broker
        state.on_broker_connection_status_changed(False)
        assert not state.connected_to_broker
        state.on_broker_connection_status_changed(True)
        state.on_disconnected()
        assert not state.connected_to_broker

    def test_return_account_information(self):
        """Should return account information."""
        assert not state.account_information
        state.on_account_information_updated({'balance': 1000})
        assert state.account_information == {'balance': 1000}

    def test_return_positions(self):
        """Should return positions."""
        assert len(state.positions) == 0
        state.on_position_updated({'id': '1', 'profit': 10})
        state.on_position_updated({'id': '2'})
        state.on_position_updated({'id': '1', 'profit': 11})
        assert len(state.positions) == 2
        state.on_position_removed('2')
        assert len(state.positions) == 1
        assert state.positions == [{'id': '1', 'profit': 11}]

    def test_return_orders(self):
        """Should return orders."""
        assert len(state.orders) == 0
        state.on_order_updated({'id': '1', 'openPrice': 10})
        state.on_order_updated({'id': '2'})
        state.on_order_updated({'id': '1', 'openPrice': 11})
        assert len(state.orders) == 2
        state.on_order_completed('2')
        assert len(state.orders) == 1
        assert state.orders == [{'id': '1', 'openPrice': 11}]

    def test_return_specifications(self):
        """Should return specifications."""
        assert len(state.specifications) == 0
        state.on_symbol_specification_updated({'symbol': 'EURUSD', 'tickSize': 0.00001})
        state.on_symbol_specification_updated({'symbol': 'GBPUSD'})
        state.on_symbol_specification_updated({'symbol': 'EURUSD', 'tickSize': 0.0001})
        assert len(state.specifications) == 2
        assert state.specifications == [{'symbol': 'EURUSD', 'tickSize': 0.0001}, {'symbol': 'GBPUSD'}]
        assert state.specification('EURUSD') == {'symbol': 'EURUSD', 'tickSize': 0.0001}

    def test_return_price(self):
        """Should return price."""
        assert not state.price('EURUSD')
        state.on_symbol_price_updated({'symbol': 'EURUSD', 'bid': 1, 'ask': 1.1})
        state.on_symbol_price_updated({'symbol': 'GBPUSD'})
        state.on_symbol_price_updated({'symbol': 'EURUSD', 'bid': 1, 'ask': 1.2})
        assert state.price('EURUSD') == {'symbol': 'EURUSD', 'bid': 1, 'ask': 1.2}

    def test_update_account_equity_and_position(self):
        """Should update account equity and position profit on price update."""
        state.on_account_information_updated({'equity': 1000})
        state.on_position_updated({
            'id': '1',
            'symbol': 'EURUSD',
            'type': 'POSITION_TYPE_BUY',
            'currentPrice': 9,
            'currentTickValue': 0.5,
            'openPrice': 8,
            'profit': 100,
            'volume': 2
        })
        state.on_position_updated({
            'id': '2',
            'symbol': 'AUDUSD',
            'type': 'POSITION_TYPE_BUY',
            'currentPrice': 9,
            'currentTickValue': 0.5,
            'openPrice': 8,
            'profit': 100,
            'volume': 10
        })
        state.on_symbol_specification_updated({'symbol': 'EURUSD', 'tickSize': 0.01})
        state.on_symbol_price_updated({
            'symbol': 'EURUSD',
            'profitTickValue': 0.5,
            'lossTickValue': 0.5,
            'bid': 10,
            'ask': 11
        })
        assert list(map(lambda p: p['profit'], state.positions)) == [200, 100]
        assert list(map(lambda p: p['currentPrice'], state.positions)) == [10, 9]
        assert state.account_information['equity'] == 1100
