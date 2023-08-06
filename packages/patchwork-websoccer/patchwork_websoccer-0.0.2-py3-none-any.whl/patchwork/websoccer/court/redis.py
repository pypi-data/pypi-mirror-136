# -*- coding: utf-8 -*-
from typing import Mapping

import aioredis
from pydantic import RedisDsn

from patchwork.websoccer.court.base import CourtClient, Record, Court


class PubSubClient(CourtClient):

    def __init__(self, redis: aioredis.Redis, data: Mapping):
        self.pubsub = redis.pubsub()
        super().__init__(data)

    def __aenter__(self):
        return self.pubsub.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.pubsub.__aexit__(exc_type, exc_val, exc_tb)
        await self.pubsub.close()

    async def subscribe(self, *topic: str):
        await self.pubsub.subscribe(*topic)

    async def unsubscribe(self, *topic: str):
        await self.pubsub.unsubscribe(*topic)

    async def get(self) -> Record:
        message = await self.pubsub.get_message(ignore_subscribe_messages=True)
        return Record(
            topic=message['channel'],
            payload=message['data']
        )


class RedisPubSubCourt(Court):
    """
    Redis based court for WebSoccer which uses pub sub queues.
    """
    class Config(Court.Config):
        redis: RedisDsn

    redis: aioredis.Redis

    async def _start(self) -> bool:
        self.redis = aioredis.Redis.from_url(self.settings.redis)
        return True

    async def _stop(self) -> bool:
        await self.redis.close()
        del self.redis
        return True

    async def publish(self, record: Record):
        await self.redis.publish(record.topic, record.payload)

    async def client(self, data: Mapping = None) -> PubSubClient:
        return PubSubClient(self.redis, data)
