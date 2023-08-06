# -*- coding: utf-8 -*-
import asyncio
from collections import defaultdict
from fnmatch import fnmatch
from typing import Mapping, Set

from patchwork.websoccer.court.base import Court, CourtClient, Record


class LocalClient(CourtClient):
    """
    Client for local court.

    For testing and debug purposes only! Local client keeps all data in local memory.
    """

    def __init__(self, channels, auth=None, permissions=None):
        self._channels = channels
        super().__init__(auth, permissions)
        self._topics = set()
        self._waiter = None

    async def subscribe(self, *topic: str):
        await super().subscribe(*topic)
        self._topics.update(topic)

        if self._waiter is not None:
            for t in topic:
                self._channels[t].add(self._waiter)

    async def unsubscribe(self, *topic: str):
        to_remove = []
        for t in topic:
            for n in self._topics:
                if fnmatch(n, t):
                    to_remove.append(n)

        self._topics.difference_update(to_remove)
        if self._waiter is not None:
            for t in to_remove:
                self._channels[t].remove(self._waiter)

    async def get(self) -> Record:
        loop = asyncio.get_running_loop()
        fut = loop.create_future()

        for topic in self._topics:
            self._channels[topic].add(fut)

        self._waiter = fut
        try:
            return await fut
        finally:
            for topic in self._topics:
                self._channels[topic].remove(fut)


class LocalCourt(Court):
    """
    Local memory court.

    For testing and debug purposes only! Local court keeps all data in local memory.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._channels: Mapping[str, Set[asyncio.Future]] = defaultdict(set)

    async def publish(self, record: Record):
        for c_name, channel in self._channels.items():
            if not fnmatch(record.topic, c_name):
                continue

            for fut in channel:
                fut.set_result(record)

    async def client(self, auth=None, permissions=None) -> CourtClient:
        return LocalClient(self._channels, auth, permissions)
