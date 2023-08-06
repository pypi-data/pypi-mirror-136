# -*- coding: utf-8 -*-
from typing import Type

from patchwork.core.config import ComponentConfig
from patchwork.node.core.dependencies import Dependency, Context
from patchwork.websoccer.court.base import Court, CourtClient

CourtConfig = ComponentConfig[Type[Court]]


class GetCourt(Dependency):

    def __init__(self, mod_name: str = 'websoccer'):
        self._name = mod_name

    def resolve(self, ctx: Context) -> Court:
        return ctx.worker.modules[self._name]


async def ws_protocol_handler(data: str, client: CourtClient) -> str:
    """
    Websocket subscriptions protocol handler
    :param data:
    :param client:
    :return:
    """
    cmd, payload = data.split(' ', maxsplit=1)
    if cmd == 'SUBSCRIBE':
        # subscribe, eg. SUBSCRIBE channel-*,private-1
        await client.subscribe(*tuple(arg.strip() for arg in payload.split(',')))
    elif cmd == 'UNSUBSCRIBE':
        # unsubscribe, eg UNSUBSCRIBE channel-1; UNSUBSCRIBE *  (all)
        await client.unsubscribe(*tuple(arg.strip() for arg in payload.split(',')))

    return 'OK'
