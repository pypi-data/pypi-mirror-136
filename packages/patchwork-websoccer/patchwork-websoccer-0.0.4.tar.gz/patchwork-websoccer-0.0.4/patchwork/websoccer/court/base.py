# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Any, Callable, Awaitable

from patchwork.core import Component


@dataclass
class Record:
    topic: str
    payload: bytes


async def all_allowed(auth, topic):
    return True


class CourtClient:

    def __init__(self, auth: Any = None, permissions: Callable[[Any, str], Awaitable[bool]] = None):
        self.auth = auth
        self.permissions = permissions or all_allowed

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def subscribe(self, *topic: str):
        """
        Subscribes for given topics on the court. * and ? patterns (fnmatch compatible) allowed
        :param topic:
        :return:
        """
        for t in topic:
            if not await self.permissions(self.auth, t):
                raise PermissionError(t)

    async def unsubscribe(self, *topic: str):
        """
        Unsubscribes on given topics on the court. * and ? patterns (fnmatch compatible) allowed
        :param topic:
        :return:
        """
        raise NotImplementedError()

    async def __aiter__(self):
        return self

    async def __anext__(self) -> Record:
        return await self.get()

    async def get(self) -> Record:
        raise NotImplementedError()


class Court(Component):
    async def publish(self, record: Record):
        raise NotImplementedError()

    async def client(self, auth: Any = None, permissions: Callable[[Any, str], Awaitable[bool]] = None) -> CourtClient:
        raise NotImplementedError()

