from .clients.synchronizationListener import SynchronizationListener
from .models import MetatraderOrder, MetatraderDeal
from datetime import datetime
from abc import abstractmethod, ABC


class HistoryStorage(SynchronizationListener, ABC):
    """ Abstract class which defines MetaTrader history storage interface.

    This class is intended to be used when account synchronization mode is set to user. In this case the consumer is
    responsible for locally maintaining a copy of MetaTrader terminal history, and the API will send only history
    changes to the consumer.
    """

    def __init__(self):
        """Inits the history storage"""
        super().__init__()
        self._orderSynchronizationFinished = False
        self._dealSynchronizationFinished = False

    @property
    def order_synchronization_finished(self) -> bool:
        """Returns flag indicating whether order history synchronization has finished.

        Returns:
            A flag indicating whether order history synchronization has finished.
        """
        return self._orderSynchronizationFinished

    @property
    def deal_synchronization_finished(self) -> bool:
        """Returns flag indicating whether deal history synchronization has finished.

        Returns:
            A flag indicating whether order history synchronization has finished.
        """
        return self._dealSynchronizationFinished

    @abstractmethod
    async def last_history_order_time(self) -> datetime:
        """Returns the time of the last history order record stored in the history storage.

        Returns:
            The time of the last history order record stored in the history storage.
        """
        pass

    @abstractmethod
    async def last_deal_time(self) -> datetime:
        """Returns the time of the last history deal record stored in the history storage.

        Returns:
            The time of the last history deal record stored in the history storage.
        """
        pass

    @abstractmethod
    async def on_history_order_added(self, history_order: MetatraderOrder):
        """Invoked when a new MetaTrader history order is added.

        Args:
            history_order: New MetaTrader history order.

        Returns:
            A coroutine which resolves when the asynchronous event is processed.
        """
        pass

    @abstractmethod
    async def on_deal_added(self, deal: MetatraderDeal):
        """Invoked when a new MetaTrader history deal is added.

        Args:
            deal: New MetaTrader history deal.

        Returns:
            A coroutine which resolves when the asynchronous event is processed.
        """
        pass

    async def on_deal_synchronization_finished(self, synchronization_id: str):
        """Invoked when a synchronization of history deals on a MetaTrader account have finished.

        Args:
            synchronization_id: Synchronization request id.

        Returns:
            A coroutine which resolves when the asynchronous event is processed.
        """
        self._dealSynchronizationFinished = True

    async def on_order_synchronization_finished(self, synchronization_id: str):
        """Invoked when a synchronization of history orders on a MetaTrader account have finished.

        Args:
            synchronization_id: Synchronization request id.

        Returns:
             A coroutine which resolves when the asynchronous event is processed
        """
        self._orderSynchronizationFinished = True

    async def on_connected(self):
        """Invoked when connection to MetaTrader terminal established."""
        self._orderSynchronizationFinished = False
        self._dealSynchronizationFinished = False
