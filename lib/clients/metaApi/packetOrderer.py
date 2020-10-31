import asyncio
from typing import Dict, List
from datetime import datetime


class PacketOrderer:
    """Class which orders the synchronization packets."""

    def __init__(self, out_of_order_listener, ordering_timeout_in_seconds: float = 10):
        """Inits the class.

        Args:
            out_of_order_listener: A function which will receive out of order packet events.
            ordering_timeout_in_seconds: Packet ordering timeout.
        """
        self._outOfOrderListener = out_of_order_listener
        self._orderingTimeoutInSeconds = ordering_timeout_in_seconds
        self._isOutOfOrderEmitted = {}
        self._waitListSizeLimit = 100
        self._outOfOrderInterval = None

    def start(self):
        """Initializes the packet orderer"""
        self._sequenceNumberByAccount = {}
        self._lastSessionStartTimestamp = {}
        self._packetsByAccountId = {}

        async def emit_events():
            while True:
                await asyncio.sleep(1)
                self._emit_out_of_order_events()

        if not self._outOfOrderInterval:
            self._outOfOrderInterval = asyncio.create_task(emit_events())

    def stop(self):
        """Deinitializes the packet orderer."""
        self._outOfOrderInterval.cancel()
        self._outOfOrderInterval = None

    def restore_order(self, packet: Dict) -> List[Dict]:
        """Processes the packet and resolves in the order of packet sequence number.

        Args:
            packet: Packet to process.

        """
        if 'sequenceNumber' not in packet:
            return [packet]
        if packet['type'] == 'specifications' and 'synchronizationId' in packet:
            # synchronization packet sequence just started
            self._isOutOfOrderEmitted[packet['accountId']] = False
            self._sequenceNumberByAccount[packet['accountId']] = packet['sequenceNumber']
            self._lastSessionStartTimestamp[packet['accountId']] = packet['sequenceTimestamp']
            self._packetsByAccountId[packet['accountId']] = \
                list(filter(lambda wait_packet: wait_packet['packet']['sequenceTimestamp'] >=
                            packet['sequenceTimestamp'],
                            (self._packetsByAccountId[packet['accountId']] if packet['accountId'] in
                             self._packetsByAccountId else [])))
            return [packet] + self._find_next_packets_from_wait_list(packet['accountId'])
        elif packet['accountId'] in self._lastSessionStartTimestamp and \
                packet['sequenceTimestamp'] < self._lastSessionStartTimestamp[packet['accountId']]:
            # filter out previous packets
            return []
        elif packet['accountId'] in self._sequenceNumberByAccount and \
                packet['sequenceNumber'] == self._sequenceNumberByAccount[packet['accountId']]:
            # let the duplicate s/n packet to pass through
            return [packet]
        elif packet['accountId'] in self._sequenceNumberByAccount and \
                packet['sequenceNumber'] == self._sequenceNumberByAccount[packet['accountId']] + 1:
            # in-order packet was received
            self._sequenceNumberByAccount[packet['accountId']] += 1
            return [packet] + self._find_next_packets_from_wait_list(packet['accountId'])
        else:
            # out-of-order packet was received, add it to the wait list
            self._packetsByAccountId[packet['accountId']] = self._packetsByAccountId[packet['accountId']] \
                if packet['accountId'] in self._packetsByAccountId else []
            wait_list = self._packetsByAccountId[packet['accountId']]
            wait_list.append({
                'accountId': packet['accountId'],
                'sequenceNumber': packet['sequenceNumber'],
                'packet': packet,
                'receivedAt': datetime.now()
            })
            wait_list.sort(key=lambda i: i['sequenceNumber'])
            while len(wait_list) > self._waitListSizeLimit:
                wait_list.pop(0)
            return []

    def _find_next_packets_from_wait_list(self, account_id) -> List:
        result = []
        wait_list = self._packetsByAccountId[account_id] if account_id in self._packetsByAccountId else []
        while len(wait_list) and wait_list[0]['sequenceNumber'] in [self._sequenceNumberByAccount[account_id],
                                                                    self._sequenceNumberByAccount[account_id] + 1]:
            result.append(wait_list[0]['packet'])
            if wait_list[0]['sequenceNumber'] == self._sequenceNumberByAccount[account_id] + 1:
                self._sequenceNumberByAccount[account_id] += 1
            wait_list.pop(0)
        if not len(wait_list) and account_id in self._packetsByAccountId:
            del self._packetsByAccountId[account_id]
        return result

    def _emit_out_of_order_events(self):
        for key, wait_list in self._packetsByAccountId.items():
            if len(wait_list) and \
                    (wait_list[0][
                         'receivedAt'].timestamp() + self._orderingTimeoutInSeconds) < datetime.now().timestamp():
                account_id = wait_list[0]['accountId']
                if account_id not in self._isOutOfOrderEmitted or not self._isOutOfOrderEmitted[account_id]:
                    self._isOutOfOrderEmitted[account_id] = True
                    self._outOfOrderListener.on_out_of_order_packet(
                        wait_list[0]['accountId'], (self._sequenceNumberByAccount[account_id] if account_id in
                                                    self._sequenceNumberByAccount else 0) + 1,
                        wait_list[0]['sequenceNumber'],
                        wait_list[0]['packet'], wait_list[0]['receivedAt'])
