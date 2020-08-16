from .memoryHistoryStorage import MemoryHistoryStorage
from .models import date
from mock import AsyncMock
from datetime import datetime
import pytest
storage = None


@pytest.fixture(autouse=True)
async def run_around_tests(mocker):
    global storage
    storage = MemoryHistoryStorage('accountId')
    await storage.on_connected()
    yield


class TestMemoryHistoryStorage:
    @pytest.mark.asyncio
    async def test_load_data_from_file_manager(self):
        """Should load data from the file manager."""
        test_deal = {'id': '37863643', 'type': 'DEAL_TYPE_BALANCE', 'magic': 0, 'time':
                     datetime.fromtimestamp(100).isoformat(),
                     'commission': 0, 'swap': 0, 'profit': 10000, 'platform': 'mt5', 'comment': 'Demo deposit 1'}
        test_order = {'id': '61210463', 'type': 'ORDER_TYPE_SELL', 'state': 'ORDER_STATE_FILLED', 'symbol': 'AUDNZD',
                      'magic': 0, 'time': datetime.fromtimestamp(50).isoformat(), 'doneTime':
                          datetime.fromtimestamp(100).isoformat(), 'currentPrice': 1, 'volume': 0.01,
                      'currentVolume': 0,
                      'positionId': '61206630', 'platform': 'mt5', 'comment': 'AS_AUDNZD_5YyM6KS7Fv:'}
        storage._fileManager.get_history_from_disk = AsyncMock(return_value={'deals': [test_deal],
                                                                             'historyOrders': [test_order]})
        await storage.load_data_from_disk()
        assert storage.deals == [test_deal]
        assert storage.history_orders == [test_order]

    @pytest.mark.asyncio
    async def test_update_disk_storage(self):
        """Should update disk storage."""

        storage._fileManager.update_disk_storage = AsyncMock()
        await storage.update_disk_storage()
        storage._fileManager.update_disk_storage.assert_called()

    @pytest.mark.asyncio
    async def test_return_last_history_order_time(self):
        """Should return last history order time."""

        await storage.on_history_order_added({'id': '1'})
        await storage.on_history_order_added({'id': '2', 'doneTime': date('2020-01-01T00:00:00.000Z')})
        await storage.on_history_order_added({'id': '3', 'doneTime': date('2020-01-02T00:00:00.000Z')})
        assert await storage.last_history_order_time() == date('2020-01-02T00:00:00.000Z')

    @pytest.mark.asyncio
    async def test_return_last_deal_time(self):
        """Should return last deal time."""

        await storage.on_deal_added({'id': '1'})
        await storage.on_deal_added({'id': '2', 'time': date('2020-01-01T00:00:00.000Z')})
        await storage.on_deal_added({'id': '3', 'time': date('2020-01-02T00:00:00.000Z')})
        assert await storage.last_deal_time() == date('2020-01-02T00:00:00.000Z',)

    @pytest.mark.asyncio
    async def test_return_saved_deals(self):
        """Should return saved deals."""

        await storage.on_deal_added({'id': '1', 'time': date('2020-01-01T00:00:00.000Z'), 'type': 'DEAL_TYPE_SELL'})
        await storage.on_deal_added({'id': '7', 'time': date('2020-05-01T00:00:00.000Z'), 'type': 'DEAL_TYPE_BUY'})
        await storage.on_deal_added({'id': '8', 'time': date('2020-02-01T00:00:00.000Z'), 'type': 'DEAL_TYPE_SELL'})
        await storage.on_deal_added({'id': '6', 'time': date('2020-10-01T00:00:00.000Z'), 'type': 'DEAL_TYPE_BUY'})
        await storage.on_deal_added({'id': '4', 'time': date('2020-02-01T00:00:00.000Z'), 'type': 'DEAL_TYPE_SELL'})
        await storage.on_deal_added({'id': '5', 'time': date('2020-06-01T00:00:00.000Z'), 'type': 'DEAL_TYPE_BUY'})
        await storage.on_deal_added({'id': '11', 'type': 'DEAL_TYPE_SELL'})
        await storage.on_deal_added({'id': '3', 'time': date('2020-09-01T00:00:00.000Z'), 'type': 'DEAL_TYPE_BUY'})
        await storage.on_deal_added({'id': '2', 'time': date('2020-08-01T00:00:00.000Z'), 'type': 'DEAL_TYPE_SELL'})
        await storage.on_deal_added({'id': '10', 'type': 'DEAL_TYPE_SELL'})
        await storage.on_deal_added({'id': '12', 'type': 'DEAL_TYPE_BUY'})

        assert storage.deals == [
            {'id': '10', 'type': 'DEAL_TYPE_SELL'},
            {'id': '11', 'type': 'DEAL_TYPE_SELL'},
            {'id': '12', 'type': 'DEAL_TYPE_BUY'},
            {'id': '1', 'time': date('2020-01-01T00:00:00.000Z'), 'type': 'DEAL_TYPE_SELL'},
            {'id': '4', 'time': date('2020-02-01T00:00:00.000Z'), 'type': 'DEAL_TYPE_SELL'},
            {'id': '8', 'time': date('2020-02-01T00:00:00.000Z'), 'type': 'DEAL_TYPE_SELL'},
            {'id': '7', 'time': date('2020-05-01T00:00:00.000Z'), 'type': 'DEAL_TYPE_BUY'},
            {'id': '5', 'time': date('2020-06-01T00:00:00.000Z'), 'type': 'DEAL_TYPE_BUY'},
            {'id': '2', 'time': date('2020-08-01T00:00:00.000Z'), 'type': 'DEAL_TYPE_SELL'},
            {'id': '3', 'time': date('2020-09-01T00:00:00.000Z'), 'type': 'DEAL_TYPE_BUY'},
            {'id': '6', 'time': date('2020-10-01T00:00:00.000Z'), 'type': 'DEAL_TYPE_BUY'}
        ]

    @pytest.mark.asyncio
    async def test_return_saved_history_orders(self):
        """Should return saved historyOrders."""

        await storage.on_history_order_added({'id': '1', 'doneTime': date('2020-01-01T00:00:00.000Z'),
                                              'type': 'ORDER_TYPE_SELL'})
        await storage.on_history_order_added({'id': '7', 'doneTime': date('2020-05-01T00:00:00.000Z'),
                                              'type': 'ORDER_TYPE_BUY'})
        await storage.on_history_order_added({'id': '8', 'doneTime': date('2020-02-01T00:00:00.000Z'),
                                              'type': 'ORDER_TYPE_SELL'})
        await storage.on_history_order_added({'id': '6', 'doneTime': date('2020-10-01T00:00:00.000Z'),
                                              'type': 'ORDER_TYPE_BUY'})
        await storage.on_history_order_added({'id': '4', 'doneTime': date('2020-02-01T00:00:00.000Z'),
                                              'type': 'ORDER_TYPE_SELL'})
        await storage.on_history_order_added({'id': '5', 'doneTime': date('2020-06-01T00:00:00.000Z'),
                                              'type': 'ORDER_TYPE_BUY'})
        await storage.on_history_order_added({'id': '11', 'type': 'ORDER_TYPE_SELL'})
        await storage.on_history_order_added({'id': '3', 'doneTime': date('2020-09-01T00:00:00.000Z'),
                                              'type': 'ORDER_TYPE_BUY'})
        await storage.on_history_order_added({'id': '2', 'doneTime': date('2020-08-01T00:00:00.000Z'),
                                              'type': 'ORDER_TYPE_SELL'})
        await storage.on_history_order_added({'id': '10', 'type': 'ORDER_TYPE_SELL'})
        await storage.on_history_order_added({'id': '12', 'type': 'ORDER_TYPE_BUY'})

        assert storage.history_orders == [
            {'id': '10', 'type': 'ORDER_TYPE_SELL'},
            {'id': '11', 'type': 'ORDER_TYPE_SELL'},
            {'id': '12', 'type': 'ORDER_TYPE_BUY'},
            {'id': '1', 'doneTime': date('2020-01-01T00:00:00.000Z'), 'type': 'ORDER_TYPE_SELL'},
            {'id': '4', 'doneTime': date('2020-02-01T00:00:00.000Z'), 'type': 'ORDER_TYPE_SELL'},
            {'id': '8', 'doneTime': date('2020-02-01T00:00:00.000Z'), 'type': 'ORDER_TYPE_SELL'},
            {'id': '7', 'doneTime': date('2020-05-01T00:00:00.000Z',), 'type': 'ORDER_TYPE_BUY'},
            {'id': '5', 'doneTime': date('2020-06-01T00:00:00.000Z'), 'type': 'ORDER_TYPE_BUY'},
            {'id': '2', 'doneTime': date('2020-08-01T00:00:00.000Z'), 'type': 'ORDER_TYPE_SELL'},
            {'id': '3', 'doneTime': date('2020-09-01T00:00:00.000Z'), 'type': 'ORDER_TYPE_BUY'},
            {'id': '6', 'doneTime': date('2020-10-01T00:00:00.000Z'), 'type': 'ORDER_TYPE_BUY'}
                                          ]

    @pytest.mark.asyncio
    async def test_return_saved_order_sync_status(self):
        """Should return saved order synchronization status."""

        assert not storage.order_synchronization_finished
        await storage.on_order_synchronization_finished('synchronizationId')
        assert storage.order_synchronization_finished

    @pytest.mark.asyncio
    async def test_return_saved_deal_sync_status(self):
        """Should return saved deal synchronization status."""

        assert not storage.deal_synchronization_finished
        await storage.on_deal_synchronization_finished('synchronizationId')
        assert storage.deal_synchronization_finished
