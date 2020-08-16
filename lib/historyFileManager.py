from .memoryHistoryStorageModel import MemoryHistoryStorageModel
import json
import os
import asyncio
from typing import List
from datetime import datetime


def stringify(obj: dict or List) -> str:
    """Helper function to convert an object to string and compress.

    Returns:
        Stringified and compressed object.
    """
    return json.dumps(obj).replace('": ', '":').replace('}, {', '},{').replace(', "', ',"')


class HistoryFileManager:
    """History storage file manager which saves and loads history on disk."""

    def __init__(self, account_id: str, history_storage: MemoryHistoryStorageModel = None):
        """Constructs the history file manager instance."""
        self._accountId = account_id
        self._historyStorage = history_storage
        self._dealsSize = []
        self._startNewDealIndex = -1
        self._historyOrdersSize = []
        self._startNewOrderIndex = -1
        self.update_disk_storage_job = None

    def start_update_job(self):
        """Starts a job to periodically save history on disk"""

        async def update_job():
            while True:
                await asyncio.sleep(60)
                await self.update_disk_storage()

        if not self.update_disk_storage_job:
            self.update_disk_storage_job = asyncio.create_task(update_job())

    def stop_update_job(self):
        """Stops a job to periodically save history on disk."""

        self.update_disk_storage_job.cancel()
        self.update_disk_storage_job = None

    def get_item_size(self, item: dict) -> int:
        """Helper function to calculate object size in bytes in utf-8 encoding.

        Returns:
            Size of object in bytes.
        """
        return len(stringify(item).encode('utf-8'))

    def set_start_new_order_index(self, index: int):
        """Sets the index of the earliest changed historyOrder record.

        Args:
            index: Index of the earliest changed record.
        """
        if self._startNewOrderIndex > index or self._startNewOrderIndex == -1:
            self._startNewOrderIndex = index

    def set_start_new_deal_index(self, index: int):
        """Sets the index of the earliest changed deal record.

        Args:
            index: Index of the earliest changed record.
        """
        if self._startNewDealIndex > index or self._startNewDealIndex == -1:
            self._startNewDealIndex = index

    async def get_history_from_disk(self):
        """Retrieves history from saved file.

        Returns:
            A coroutine resolving with an object with deals and historyOrders.
        """

        history = {'deals': [], 'historyOrders': []}
        try:
            if os.path.isfile(f'.metaapi/{self._accountId}-deals.bin'):
                deals = json.loads(open(f'.metaapi/{self._accountId}-deals.bin').read())
                self._dealsSize = list(map(self.get_item_size, deals))
                history['deals'] = deals
        except Exception as err:
            print(f'[{datetime.now().isoformat()}] Failed to read deals history storage of '
                  f'account {self._accountId}', err)
            os.remove(f'.metaapi/{self._accountId}-deals.bin')

        try:
            if os.path.isfile(f'.metaapi/{self._accountId}-historyOrders.bin'):
                history_orders = json.loads(open(f'.metaapi/{self._accountId}-historyOrders.bin').read())
                self._historyOrdersSize = list(map(self.get_item_size, history_orders))
                history['historyOrders'] = history_orders
        except Exception as err:
            print(f'[{datetime.now().isoformat()}] Failed to read historyOrders history storage of '
                  f'account {self._accountId}', err)
            os.remove(f'.metaapi/{self._accountId}-historyOrders.bin')
        return history

    async def update_disk_storage(self):
        """Saves unsaved history items to disk storage.

        Returns:
            A coroutine resolving when the history is saved to disk.
        """

        account_id = self._accountId
        if not os.path.exists('.metaapi'):
            os.mkdir('.metaapi')

        async def replace_records(history_type, start_index: int, replace_items: List, size_array: List) -> List[int]:
            file_path = f'.metaapi/{account_id}-{history_type}.bin'
            file_size = os.path.getsize(file_path)
            if start_index == 0:
                f = open(file_path, 'w+')
                f.write(stringify(replace_items))
                f.close()
            else:
                f = open(file_path, 'a+')
                replaced_items = size_array[start_index:]
                start_position = file_size - len(replaced_items) - sum(replaced_items) - 1
                f.seek(start_position)
                f.truncate()
                f.close()
                f = open(file_path, "a+")
                f.write(',' + stringify(replace_items)[1:])
                f.close()
            return size_array[0:start_index] + list(map(self.get_item_size, replace_items))

        if self._startNewDealIndex != -1:
            if not os.path.isfile(f'.metaapi/{account_id}-deals.bin'):
                try:
                    f = open(f'.metaapi/{account_id}-deals.bin', "w+")
                    f.write(stringify(self._historyStorage.deals))
                    f.close()
                except Exception as err:
                    print(f'[{datetime.now().isoformat()}] Error saving deals on disk for account {self._accountId}',
                          err)
                self._dealsSize = list(map(self.get_item_size, self._historyStorage.deals))
            else:
                replace_deals = self._historyStorage.deals[self._startNewDealIndex:]
                self._dealsSize = await replace_records('deals', self._startNewDealIndex, replace_deals,
                                                        self._dealsSize)
            self._startNewDealIndex = -1

        if self._startNewOrderIndex != -1:
            if not os.path.isfile(f'.metaapi/{account_id}-historyOrders.bin'):
                try:
                    f = open(f'.metaapi/{account_id}-historyOrders.bin', "w+")
                    f.write(stringify(self._historyStorage.history_orders))
                    f.close()
                except Exception as err:
                    print(f'[{datetime.now().isoformat()}] Error saving historyOrders on disk for '
                          f'account {account_id}', err)
                self._historyOrdersSize = list(map(self.get_item_size, self._historyStorage.history_orders))
            else:
                replace_orders = self._historyStorage.history_orders[self._startNewOrderIndex:]
                self._historyOrdersSize = await replace_records('historyOrders', self._startNewOrderIndex,
                                                                replace_orders, self._historyOrdersSize)
            self._startNewOrderIndex = -1

    async def delete_storage_from_disk(self):
        """Deletes storage files from disk.

        Returns:
            A coroutine resolving when the history is deleted from disk.
        """

        if os.path.isfile(f'.metaapi/{self._accountId}-deals.bin'):
            os.remove(f'.metaapi/{self._accountId}-deals.bin')
        if os.path.isfile(f'.metaapi/{self._accountId}-historyOrders.bin'):
            os.remove(f'.metaapi/{self._accountId}-historyOrders.bin')
