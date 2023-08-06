# -*- coding: utf-8 -*-
import asyncio

import pytest as pytest

from patchwork.websoccer.court.base import Record
from patchwork.websoccer.court.local import LocalCourt


@pytest.mark.asyncio
async def test_direct_queue():
    court = LocalCourt()

    client = await court.client()

    await client.subscribe('topic-1')
    record = None

    async def _listen():
        nonlocal record
        record = await client.__anext__()

    listen = asyncio.create_task(_listen())

    # sleep to allow event loop to run pending tasks, like _listen and register
    # listening futures
    await asyncio.sleep(0)

    await court.publish(Record(
        topic='topic-1',
        payload=b'test-payload'
    ))

    # add wait for, so test won't hang up if something went wrong and client never receive
    # a message, 0 timeout is enough, as 0 should allow event loop to run all pending tasks
    await asyncio.wait_for(listen, 100)

    assert record.topic == 'topic-1'
    assert record.payload == b'test-payload'


