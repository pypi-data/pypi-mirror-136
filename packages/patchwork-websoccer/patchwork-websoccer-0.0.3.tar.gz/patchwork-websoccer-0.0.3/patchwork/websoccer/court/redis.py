# -*- coding: utf-8 -*-
import logging
from typing import Mapping

import aioredis
from pydantic import RedisDsn

from patchwork.websoccer.court.base import CourtClient, Record, Court


logger = logging.getLogger('patchwork.websoccer.redis')


class PubSubClient(CourtClient):

    def __init__(self, redis: aioredis.Redis, data: Mapping):
        self.pubsub = redis.pubsub()
        logger.debug("Client attached")
        super().__init__(data)

    def __aenter__(self):
        return self.pubsub.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.pubsub.__aexit__(exc_type, exc_val, exc_tb)
        await self.pubsub.close()

    async def subscribe(self, *topic: str):
        await self.pubsub.subscribe(*topic)
        logger.debug(f"subscribe on {', '.join(topic)}")

    async def unsubscribe(self, *topic: str):
        await self.pubsub.unsubscribe(*topic)
        logger.debug(f"unsubscribe from {', '.join(topic)}")

    async def get(self) -> Record:
        message = await self.pubsub.get_message(ignore_subscribe_messages=True)
        return Record(
            topic=message['channel'],
            payload=message['data']
        )

    def __repr__(self):
        res = super().__repr__()
        return f"{res[:-1]} {self.pubsub.connection_pool!r} for {','.join(self.pubsub.channels.keys())}>"


class RedisPubSubCourt(Court):
    """
    Redis based court for WebSoccer which uses pub sub queues.
    """
    class Config(Court.Config):
        redis: RedisDsn

    redis: aioredis.Redis

    async def _start(self) -> bool:
        self.redis = aioredis.Redis.from_url(self.settings.redis)
        logger.info(f"Redis Pub-Sub court initialized on {self.settings.redis}")
        return True

    async def _stop(self) -> bool:
        await self.redis.close()
        del self.redis
        return True

    async def publish(self, record: Record):
        await self.redis.publish(record.topic, record.payload)

    async def client(self, data: Mapping = None) -> PubSubClient:
        return PubSubClient(self.redis, data)

    def __repr__(self):
        res = super().__repr__()
        return f'{res[:-1]} {self.redis!r}>'
