# -*- coding: utf-8 -*-
import asyncio
from typing import cast

import pytest
from async_asgi_testclient import TestClient
from fastapi import FastAPI
from starlette import status

from patchwork.node import PatchworkWorker
from patchwork.node.core import TaskRouter
from patchwork.node.testutils import TestWorker
from patchwork.websoccer import LocalCourt, Record
from patchwork.websoccer.court.base import Court
from patchwork.websoccer.fastapi import bind_fastapi
from patchwork.websoccer.soccer import GetCourt


@pytest.mark.asyncio
async def test_simple_fastapi_usage():

    court = LocalCourt()

    app = FastAPI()
    router = bind_fastapi(court)

    app.include_router(router, prefix='/app')

    async with TestClient(app) as client:
        descr_resp = await client.get('/app')
        assert descr_resp.status_code == status.HTTP_200_OK
        assert descr_resp.json() == {
            'endpoints': {
                'websocket': '/ws'
            }
        }

        async with client.websocket_connect('/app/ws') as ws:
            await ws.send_text('SUBSCRIBE test-channel')
            resp = await ws.receive_text()
            assert resp == 'OK'

            # there should be one waiter for new subscription on internals
            assert len(court._channels['test-channel']) == 1

            # and now test if there is no side effects, this record SHOULD BE
            # delivered
            await court.publish(Record(
                topic='test-channel',
                payload=b'test-notification'
            ))

            resp = await ws.receive_text()
            assert resp == b'test-notification'

            await ws.send_text('UNSUBSCRIBE test-channel')
            resp = await ws.receive_text()
            assert resp == 'OK'

            # there should be no internal waiters after unsubscribe
            assert len(court._channels['test-channel']) == 0

            # and now test if there is no side effects, this record SHOULD NOT
            # be delivered
            await court.publish(Record(
                topic='test-channel',
                payload=b'test-notification-2'
            ))

            with pytest.raises(asyncio.TimeoutError):
                # 0 allows event loop to take control and execute all pending tasks, if there is something
                # pending to be delivered to websocket it will be and task will fail (nothing should be pending
                # as client unsubscribed)
                await asyncio.wait_for(ws.receive_text(), 0)


@pytest.mark.asyncio
async def test_simple_node_usage():

    worker_settings = {
        'modules': {
            'websoccer': {
                'engine': 'patchwork.websoccer:LocalCourt',
            }
        },
        'subscriber': {
            'engine': 'patchwork.core.client.local:AsyncLocalSubscriber',
            'queue_names': ['test-topic'],
        },
    }

    router = TaskRouter()

    @router.on()
    async def example_task(c: Court = GetCourt()):
        await c.publish(Record(
            topic='test',
            payload=b'foobar'
        ))

    worker = PatchworkWorker(settings=worker_settings)
    worker.include_router(router)
    async with TestWorker(worker) as w:
        assert 'websoccer' in worker.modules
        court: LocalCourt = cast(LocalCourt, worker.modules['websoccer'])
        assert court.is_running

        client = await court.client()
        await client.subscribe('test')
        fetcher = asyncio.create_task(client.get())

        await w.send(b'', task_type='example_task', queue_name='test-topic')
        await w.wait_once()

        r = await fetcher
        assert r.topic == 'test'
        assert r.payload == b'foobar'




