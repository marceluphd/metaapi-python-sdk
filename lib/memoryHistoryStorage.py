from lib.models import MetatraderDeal, MetatraderOrder
from typing import List
from lib.historyStorage import HistoryStorage
from datetime import datetime
import pytz


class MemoryHistoryStorage(HistoryStorage):
    """History storage which stores MetaTrader history in RAM."""

    def __init__(self):
        """Inits the in-memory history store instance"""
        super().__init__()
        self._deals = []
        self._historyOrders = []

    def reset(self):
        """Resets the storage. Intended for use in tests."""

        self._deals = []
        self._historyOrders = []

    @property
    def deals(self) -> List[MetatraderDeal]:
        """Returns all deals stored in history storage.

        Returns:
            All deals stored in history storage.
        """
        return self._deals

    @property
    def history_orders(self) -> List[MetatraderOrder]:
        """Returns all history orders stored in history storage.

        Returns:
            All history orders stored in history storage.
        """
        return self._historyOrders

    async def last_history_order_time(self) -> datetime:
        """Returns the time of the last history order record stored in the history storage.

        Returns:
            The time of the last history order record stored in the history storage
        """
        filtered_orders = list(filter(lambda order: 'doneTime' in order, self._historyOrders))
        return max(order['doneTime'] for order in (filtered_orders +
                                                   [{'doneTime': datetime.min.replace(tzinfo=pytz.UTC)}]))

    async def last_deal_time(self) -> datetime:
        """Returns the time of the last history deal record stored in the history storage.

        Returns:
            The time of the last history deal record stored in the history storage.
        """
        filtered_deals = list(filter(lambda order: 'time' in order, self._deals))
        return max(order['time'] for order in (filtered_deals +
                   [{'time': datetime.min.replace(tzinfo=pytz.UTC)}]))

    async def on_history_order_added(self, history_order: MetatraderOrder):
        """Invoked when a new MetaTrader history order is added.

        Args:
            history_order: New MetaTrader history order.
        """
        insert_index = 0
        replacement_index = -1

        def get_done_time(order):
            return order['doneTime'].timestamp() if ('doneTime' in order) else \
                datetime.min.replace(tzinfo=pytz.UTC).timestamp()

        for i in range(len(self._historyOrders)):
            order = self._historyOrders[i]
            if (get_done_time(order) < get_done_time(history_order)) or \
                    (get_done_time(order) == get_done_time(history_order) and order['id'] <= history_order['id']):
                if (get_done_time(order) == get_done_time(history_order) and order['id'] == history_order['id'] and
                   order['type'] == history_order['type']):
                    replacement_index = i
                insert_index = i + 1
        if replacement_index != -1:
            self._historyOrders[replacement_index] = history_order
        else:
            self._historyOrders.insert(insert_index, history_order)

    async def on_deal_added(self, new_deal: MetatraderDeal):
        """Invoked when a new MetaTrader history deal is added.

        Args:
            new_deal: New MetaTrader history deal.
        """
        insert_index = 0
        replacement_index = -1

        def get_time(deal):
            return deal['time'].timestamp() if ('time' in deal) else datetime.min.replace(tzinfo=pytz.UTC).timestamp()

        for i in range(len(self._deals)):
            deal = self._deals[i]
            if (get_time(deal) < get_time(new_deal)) or \
                    (get_time(deal) == get_time(new_deal) and deal['id'] <= new_deal['id']):
                if (get_time(deal) == get_time(new_deal) and deal['id'] == new_deal['id'] and
                        deal['type'] == new_deal['type']):
                    replacement_index = i
                insert_index = i + 1
        if replacement_index != -1:
            self._deals[replacement_index] = new_deal
        else:
            self._deals.insert(insert_index, new_deal)
