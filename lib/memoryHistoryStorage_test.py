from lib.memoryHistoryStorage import MemoryHistoryStorage
from lib.models import DATE_FORMAT
import pytest
import datetime
storage = MemoryHistoryStorage()


@pytest.fixture(autouse=True)
async def run_around_tests():
    storage.reset()
    storage.on_connected()
    yield


class TestMemoryHistoryStorage:
    @pytest.mark.asyncio
    async def test_return_last_history_order_time(self):
        """Should return last history order time."""

        storage.on_history_order_added({'id': '1'})
        storage.on_history_order_added({'id': '2', 'doneTime': datetime.datetime.strptime(
                                        '2020-01-01T00:00:00.000Z', DATE_FORMAT)})
        storage.on_history_order_added({'id': '3', 'doneTime': datetime.datetime.strptime(
                                        '2020-01-02T00:00:00.000Z', DATE_FORMAT)})
        assert storage.last_history_order_time() == datetime.datetime.strptime('2020-01-02T00:00:00.000Z', DATE_FORMAT)

    @pytest.mark.asyncio
    async def test_return_last_deal_time(self):
        """Should return last deal time."""

        storage.on_deal_added({'id': '1'})
        storage.on_deal_added({'id': '2', 'time': datetime.datetime.strptime(
            '2020-01-01T00:00:00.000Z', DATE_FORMAT)})
        storage.on_deal_added({'id': '3', 'time': datetime.datetime.strptime(
            '2020-01-02T00:00:00.000Z', DATE_FORMAT)})
        assert storage.last_deal_time() == datetime.datetime.strptime('2020-01-02T00:00:00.000Z', DATE_FORMAT)

    @pytest.mark.asyncio
    async def test_return_saved_deals(self):
        """Should return saved deals."""

        storage.on_deal_added({'id': '1', 'time': datetime.datetime.strptime(
            '2020-01-01T00:00:00.000Z', DATE_FORMAT), 'type': 'DEAL_TYPE_SELL'})
        storage.on_deal_added({'id': '7', 'time': datetime.datetime.strptime(
            '2020-05-01T00:00:00.000Z', DATE_FORMAT), 'type': 'DEAL_TYPE_BUY'})
        storage.on_deal_added({'id': '8', 'time': datetime.datetime.strptime(
            '2020-02-01T00:00:00.000Z', DATE_FORMAT), 'type': 'DEAL_TYPE_SELL'})
        storage.on_deal_added({'id': '6', 'time': datetime.datetime.strptime(
            '2020-10-01T00:00:00.000Z', DATE_FORMAT), 'type': 'DEAL_TYPE_BUY'})
        storage.on_deal_added({'id': '4', 'time': datetime.datetime.strptime(
            '2020-02-01T00:00:00.000Z', DATE_FORMAT), 'type': 'DEAL_TYPE_SELL'})
        storage.on_deal_added({'id': '5', 'time': datetime.datetime.strptime(
            '2020-06-01T00:00:00.000Z', DATE_FORMAT), 'type': 'DEAL_TYPE_BUY'})
        storage.on_deal_added({'id': '11', 'type': 'DEAL_TYPE_SELL'})
        storage.on_deal_added({'id': '3', 'time': datetime.datetime.strptime(
            '2020-09-01T00:00:00.000Z', DATE_FORMAT), 'type': 'DEAL_TYPE_BUY'})
        storage.on_deal_added({'id': '2', 'time': datetime.datetime.strptime(
            '2020-08-01T00:00:00.000Z', DATE_FORMAT), 'type': 'DEAL_TYPE_SELL'})
        storage.on_deal_added({'id': '10', 'type': 'DEAL_TYPE_SELL'})
        storage.on_deal_added({'id': '12', 'type': 'DEAL_TYPE_BUY'})

        assert storage.deals == [
            {'id': '10', 'type': 'DEAL_TYPE_SELL'},
            {'id': '11', 'type': 'DEAL_TYPE_SELL'},
            {'id': '12', 'type': 'DEAL_TYPE_BUY'},
            {'id': '1', 'time': datetime.datetime.strptime(
                '2020-01-01T00:00:00.000Z', DATE_FORMAT), 'type': 'DEAL_TYPE_SELL'},
            {'id': '4', 'time': datetime.datetime.strptime(
                '2020-02-01T00:00:00.000Z', DATE_FORMAT), 'type': 'DEAL_TYPE_SELL'},
            {'id': '8', 'time': datetime.datetime.strptime(
                '2020-02-01T00:00:00.000Z', DATE_FORMAT), 'type': 'DEAL_TYPE_SELL'},
            {'id': '7', 'time': datetime.datetime.strptime(
                '2020-05-01T00:00:00.000Z', DATE_FORMAT), 'type': 'DEAL_TYPE_BUY'},
            {'id': '5', 'time': datetime.datetime.strptime(
                '2020-06-01T00:00:00.000Z', DATE_FORMAT), 'type': 'DEAL_TYPE_BUY'},
            {'id': '2', 'time': datetime.datetime.strptime(
                '2020-08-01T00:00:00.000Z', DATE_FORMAT), 'type': 'DEAL_TYPE_SELL'},
            {'id': '3', 'time': datetime.datetime.strptime(
                '2020-09-01T00:00:00.000Z', DATE_FORMAT), 'type': 'DEAL_TYPE_BUY'},
            {'id': '6', 'time': datetime.datetime.strptime(
                '2020-10-01T00:00:00.000Z', DATE_FORMAT), 'type': 'DEAL_TYPE_BUY'}
        ]

    @pytest.mark.asyncio
    async def test_return_saved_history_orders(self):
        """Should return saved historyOrders."""

        storage.on_history_order_added({'id': '1', 'doneTime':  datetime.datetime.strptime(
                                        '2020-01-01T00:00:00.000Z', DATE_FORMAT), 'type': 'ORDER_TYPE_SELL'})
        storage.on_history_order_added({'id': '7', 'doneTime': datetime.datetime.strptime(
            '2020-05-01T00:00:00.000Z', DATE_FORMAT), 'type': 'ORDER_TYPE_BUY'})
        storage.on_history_order_added({'id': '8', 'doneTime': datetime.datetime.strptime(
            '2020-02-01T00:00:00.000Z', DATE_FORMAT), 'type': 'ORDER_TYPE_SELL'})
        storage.on_history_order_added({'id': '6', 'doneTime': datetime.datetime.strptime(
            '2020-10-01T00:00:00.000Z', DATE_FORMAT), 'type': 'ORDER_TYPE_BUY'})
        storage.on_history_order_added({'id': '4', 'doneTime': datetime.datetime.strptime(
            '2020-02-01T00:00:00.000Z', DATE_FORMAT), 'type': 'ORDER_TYPE_SELL'})
        storage.on_history_order_added({'id': '5', 'doneTime': datetime.datetime.strptime(
            '2020-06-01T00:00:00.000Z', DATE_FORMAT), 'type': 'ORDER_TYPE_BUY'})
        storage.on_history_order_added({'id': '11', 'type': 'ORDER_TYPE_SELL'})
        storage.on_history_order_added({'id': '3', 'doneTime': datetime.datetime.strptime(
            '2020-09-01T00:00:00.000Z', DATE_FORMAT), 'type': 'ORDER_TYPE_BUY'})
        storage.on_history_order_added({'id': '2', 'doneTime': datetime.datetime.strptime(
            '2020-08-01T00:00:00.000Z', DATE_FORMAT), 'type': 'ORDER_TYPE_SELL'})
        storage.on_history_order_added({'id': '10', 'type': 'ORDER_TYPE_SELL'})
        storage.on_history_order_added({'id': '12', 'type': 'ORDER_TYPE_BUY'})

        assert storage.history_orders == [
            {'id': '10', 'type': 'ORDER_TYPE_SELL'},
            {'id': '11', 'type': 'ORDER_TYPE_SELL'},
            {'id': '12', 'type': 'ORDER_TYPE_BUY'},
            {'id': '1', 'doneTime': datetime.datetime.strptime(
                '2020-01-01T00:00:00.000Z', DATE_FORMAT), 'type': 'ORDER_TYPE_SELL'},
            {'id': '4', 'doneTime': datetime.datetime.strptime(
                '2020-02-01T00:00:00.000Z', DATE_FORMAT), 'type': 'ORDER_TYPE_SELL'},
            {'id': '8', 'doneTime': datetime.datetime.strptime(
                '2020-02-01T00:00:00.000Z', DATE_FORMAT), 'type': 'ORDER_TYPE_SELL'},
            {'id': '7', 'doneTime': datetime.datetime.strptime(
                '2020-05-01T00:00:00.000Z', DATE_FORMAT), 'type': 'ORDER_TYPE_BUY'},
            {'id': '5', 'doneTime': datetime.datetime.strptime(
                '2020-06-01T00:00:00.000Z', DATE_FORMAT), 'type': 'ORDER_TYPE_BUY'},
            {'id': '2', 'doneTime': datetime.datetime.strptime(
                '2020-08-01T00:00:00.000Z', DATE_FORMAT), 'type': 'ORDER_TYPE_SELL'},
            {'id': '3', 'doneTime': datetime.datetime.strptime(
                '2020-09-01T00:00:00.000Z', DATE_FORMAT), 'type': 'ORDER_TYPE_BUY'},
            {'id': '6', 'doneTime': datetime.datetime.strptime(
                '2020-10-01T00:00:00.000Z', DATE_FORMAT), 'type': 'ORDER_TYPE_BUY'}
                                          ]

    @pytest.mark.asyncio
    async def test_return_saved_order_sync_status(self):
        """Should return saved order synchronization status."""

        assert not storage.order_synchronization_finished
        await storage.on_order_synchronization_finished()
        assert storage.order_synchronization_finished

    @pytest.mark.asyncio
    async def test_return_saved_deal_sync_status(self):
        """Should return saved deal synchronization status."""

        assert not storage.deal_synchronization_finished
        await storage.on_deal_synchronization_finished()
        assert storage.deal_synchronization_finished
