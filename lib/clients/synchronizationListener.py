from ..models import MetatraderPosition, MetatraderAccountInformation, MetatraderOrder, \
    MetatraderDeal, MetatraderSymbolSpecification, MetatraderSymbolPrice
from abc import ABC


class SynchronizationListener(ABC):
    """Defines interface for a synchronization listener class."""

    async def on_connected(self):
        """Invoked when connection to MetaTrader terminal established.

        Returns:
            A coroutine which resolves when the asynchronous event is processed.
        """
        pass

    async def on_disconnected(self):
        """Invoked when connection to MetaTrader terminal terminated.

        Returns:
             A coroutine which resolves when the asynchronous event is processed.
        """
        pass

    async def on_broker_connection_status_changed(self, connected: bool):
        """Invoked when broker connection satus have changed.

        Args:
            connected: Is MetaTrader terminal is connected to broker.

        Returns:
            A coroutine which resolves when the asynchronous event is processed.
        """
        pass

    async def on_account_information_updated(self, account_information: MetatraderAccountInformation):
        """Invoked when MetaTrader position is updated.

        Args:
            account_information: Updated MetaTrader position.

        Returns:
            A coroutine which resolves when the asynchronous event is processed.
        """
        pass

    async def on_position_updated(self, position: MetatraderPosition):
        """Invoked when MetaTrader position is updated.

        Args:
            position: Updated MetaTrader position.

        Returns:
            A coroutine which resolves when the asynchronous event is processed.
        """
        pass

    async def on_position_removed(self, position_id: str):
        """Invoked when MetaTrader position is removed.

        Args:
            position_id: Removed MetaTrader position id.

        Returns:
            A coroutine which resolves when the asynchronous event is processed.
        """
        pass

    async def on_order_updated(self, order: MetatraderOrder):
        """Invoked when MetaTrader order is updated.

        Args:
            order: Updated MetaTrader order.

        Returns:
            A coroutine which resolves when the asynchronous event is processed.
        """
        pass

    async def on_order_completed(self, order_id: str):
        """Invoked when MetaTrader order is completed (executed or canceled).

        Args:
            order_id: Completed MetaTrader order id.

        Returns:
            A coroutine which resolves when the asynchronous event is processed.
        """
        pass

    async def on_history_order_added(self, history_order: MetatraderOrder):
        """Invoked when a new MetaTrader history order is added.

        Args:
            history_order: New MetaTrader history order.

        Returns:
            A coroutine which resolves when the asynchronous event is processed.
        """
        pass

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
        pass

    async def on_order_synchronization_finished(self, synchronization_id: str):
        """Invoked when a synchronization of history orders on a MetaTrader account have finished.

        Args:
            synchronization_id: Synchronization request id.

        Returns:
             A coroutine which resolves when the asynchronous event is processed
        """
        pass

    async def on_symbol_specification_updated(self, specification: MetatraderSymbolSpecification):
        """Invoked when a symbol specification was updated

        Args:
            specification: Updated MetaTrader symbol specification.

        Returns:
            A coroutine which resolves when the asynchronous event is processed.
        """
        pass

    async def on_symbol_price_updated(self, price: MetatraderSymbolPrice):
        """Invoked when a symbol price was updated.

        Args:
            price: Updated MetaTrader symbol price.

        Returns:
            A coroutine which resolves when the asynchronous event is processed.
        """
        pass
